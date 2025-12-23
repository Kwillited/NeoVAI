// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::env;
use std::path::{Path, PathBuf};
use std::process::Command;
// 添加编码转换支持
use encoding::all::GBK;
use encoding::{DecoderTrap, Encoding};

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn execute_command(command: &str) -> Result<String, String> {
    // 特殊处理cd命令
    if command.to_lowercase().starts_with("cd ") {
        let path = &command[3..].trim();
        return match env::set_current_dir(path) {
            Ok(_) => {
                // 返回新的当前目录
                match env::current_dir() {
                    Ok(current) => Ok(format!("当前目录为: {}", current.display())),
                    Err(e) => Err(format!("无法获取当前目录: {}", e)),
                }
            }
            Err(e) => Err(format!("无法切换到目录 '{}': {}", path, e)),
        };
    }
    // 特殊处理单独的cd命令（显示当前目录）
    else if command.trim().to_lowercase() == "cd" {
        return match env::current_dir() {
            Ok(current) => Ok(format!("当前目录为: {}", current.display())),
            Err(e) => Err(format!("无法获取当前目录: {}", e)),
        };
    }

    // 对于其他命令，使用cmd.exe执行
    let output = Command::new("cmd")
        .args(["/c", command])
        .output()
        .map_err(|e| format!("执行命令失败: {}", e))?;

    // 处理命令输出的编码问题（Windows命令行通常使用GBK编码）
    let decode_output = |bytes: &[u8]| -> String {
        if bytes.is_empty() {
            return String::new();
        }

        // 尝试以UTF-8解码
        if let Ok(utf8_str) = String::from_utf8(bytes.to_vec()) {
            return utf8_str;
        }

        // 如果UTF-8解码失败，尝试以GBK解码
        match GBK.decode(bytes, DecoderTrap::Replace) {
            Ok(gbk_str) => gbk_str,
            Err(_) => {
                // 如果GBK解码也失败，使用损失最小的方式解码
                String::from_utf8_lossy(bytes).to_string()
            }
        }
    };

    let stdout = decode_output(&output.stdout);
    let stderr = decode_output(&output.stderr);

    let mut result = String::new();
    if !stdout.is_empty() {
        result.push_str(&stdout);
    }
    if !stderr.is_empty() {
        if !result.is_empty() {
            result.push_str("\n");
        }
        result.push_str(&stderr);
    }

    // 如果命令执行失败，返回错误信息
    if !output.status.success() {
        return Err(format!("命令执行失败: {}", result));
    }

    Ok(result.trim().to_string())
}

#[tauri::command]
fn start_python_server() -> Result<String, String> {
    // 获取当前可执行文件所在目录
    let exe_path = env::current_exe().map_err(|e| format!("无法获取可执行文件路径: {}", e))?;
    let exe_dir = exe_path.parent().ok_or("无法获取可执行文件所在目录")?;

    // 尝试不同的Python脚本路径（main.py）
    let mut python_script_path = exe_dir.join("python").join("main.py");

    // 如果在当前目录找不到，尝试在其他可能的位置
    if !python_script_path.exists() {
        // 尝试在可执行文件同级目录的resources子目录中查找（Tauri打包后的资源位置）
        python_script_path = exe_dir.join("resources").join("python").join("main.py");
    }

    // 如果仍找不到，尝试在应用数据目录中查找
    if !python_script_path.exists() {
        python_script_path = exe_dir.join("data").join("python").join("main.py");
    }

    // 作为最后的备选，尝试原始开发路径（当前项目路径）
    if !python_script_path.exists() {
        let current_dir = env::current_dir().map_err(|e| format!("无法获取当前目录: {}", e))?;
        let absolute_path = current_dir.join("src-tauri").join("python").join("main.py");
        if absolute_path.exists() {
            python_script_path = absolute_path.to_path_buf();
        }
    }

    if !python_script_path.exists() {
        return Err(format!("找不到Python脚本: {:?}", python_script_path));
    }

    println!("使用Python脚本路径: {:?}", python_script_path);

    // 启动Python进程
    match start_python_process(&python_script_path) {
        Ok(pid) => Ok(format!("Python服务器启动成功，进程ID: {}", pid)),
        Err(e) => Err(format!("启动Python服务器失败: {}", e)),
    }
}

fn find_python_executable() -> Result<PathBuf, String> {
    // 直接使用系统Python
    println!("使用系统Python");
    Ok(PathBuf::from("python"))
}

fn start_python_process(script_path: &Path) -> Result<String, String> {
    // 查找系统Python可执行文件
    let python_exe_path = find_python_executable()?;

    println!("使用系统Python启动脚本: {:?}", script_path);

    // 使用系统Python启动脚本
    let result = Command::new(python_exe_path)
        .arg(script_path)
        .spawn()
        .map_err(|e| format!("无法启动Python脚本: {}", e))?;

    Ok(format!("Python服务器已启动，进程ID: {}", result.id()))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_cli::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            start_python_server,
            execute_command
        ])
        .setup(|_| {
            // 应用启动时自动启动Python服务器
            match start_python_server() {
                Ok(msg) => println!("{}", msg),
                Err(e) => println!("Python服务器启动失败: {}", e),
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
