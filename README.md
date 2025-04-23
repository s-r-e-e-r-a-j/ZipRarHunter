## ZipRarHunter
ZipRarHunter is a command-line password cracking tool designed to crack passwords for ZIP and RAR archive files using a wordlist. It helps automate the process of password recovery from encrypted archive files.

## Features
- **Support for ZIP and RAR Files:** ZipRarHunter works with both ZIP and RAR archives.
- **Wordlist-based Cracking:** The tool uses a wordlist (a file containing potential passwords) to attempt cracking the password.

- **Real-time Feedback:** It shows the current password being attempted in real time, so you can track the progress.
- **Supported OS:** Linux only (Tested on Kali, Ubuntu, etc.)
## Requirements
- **Python 3.x:** Ensure that Python 3 is installed on your system.
- **Dependencies:**
- `pyzipper` (for handling ZIP files)
- `rarfile` (for handling RAR files)
  
**You can install the required Python packages using**:`pip3`
```bash
pip3 install pyzipper
```
```bash
pip3 install rarfile
```
## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/s-r-e-e-r-a-j/ZipRarHunter.git
```
2. **Navigate to the ZipRarHunter directory:**

```bash
cd ZipRarHunter
```
3. **Ensure all dependencies are installed. If not, run:**

``` bash
pip install -r requirements.txt
```

4. **Navigate to the ZipRarHunter directory**
   
```bash
cd ZipRarHunter
```
5. **Install the tool**
```bash
sudo python3 install.py
```
**then enter `y` for install**
## Usage
ZipRarHunter uses command-line arguments to specify the target file, wordlist, and file type (ZIP or RAR).

## Basic Usage
```bash
ziprarhunter -f /path/to/archive.zip -w /path/to/wordlist.txt -t zip
ziprarhunter -f /path/to/archive.rar -w /path/to/wordlist.txt -t rar
```
## Command-line Arguments
- `-f` or `--file`: The path to the ZIP or RAR file you want to crack.
- `-w` or `--wordlist`: The path to the wordlist file that contains potential passwords.
- `-t` or `--type`: The type of archive. Acceptable values are zip or rar.
- `--no-color`: Disable colored output. By default, the output will include color for easier readability.
## Example Commands
1. **Crack a ZIP file with a wordlist:**

``` bash
ziprarhunter -f /path/to/archive.zip -w /path/to/wordlist.txt -t zip
```
2. **Crack a RAR file with a wordlist:**

```bash
ziprarhunter -f /path/to/archive.rar -w /path/to/wordlist.txt -t rar
```
3. **Disable colored output:**

```bash
ziprarhunter -f /path/to/archive.zip -w /path/to/wordlist.txt -t zip --no-color
```
## Output Example
```bash
Trying password: password123
Password found for ZIP file: password123
```

## uninstallation
```bash
cd ZipRarHunter
```
```bash
cd ZipRarHunter
```
```bash
sudo python3 install.py
```
**Then Enter `n` for uninstall**

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This tool is intended for educational purposes only. It should be used responsibly and legally. Unauthorized use of this tool to crack passwords without permission is illegal and unethical.


