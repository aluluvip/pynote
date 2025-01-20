#### 一、前提：安装 Zsh
以下命令在基于 Debian 或 Ubuntu 的系统中安装：

```sudo apt -y install zsh```

设置默认shell：

```
which zsh
chsh -s /usr/bin/zsh
```

#### 二、安装 Oh My Zshs
最常见的安装方法是通过 curl 命令：66
```sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"```
也可以使用 wget 来安装：sdfsdf 
```sh -c "$(wget -O - https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"```
安装过程中，如果默认shell不是zsh，它会询问你是否要将 Zsh 设置为默认的 shell。如果同意，它会自动进行设置。
#### 三、安装常用插件
Zsh - Syntax Highlighting（语法高亮）
```git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting```
Zsh - Autosuggestions（自动建议）
```git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions```
添加到 `.zshrc` 文件中：
```sudo nano ~/.zshrc```
```plugins=(git zsh-syntax-highlighting zsh-autosuggestions)```
#### 四、配置主题
克隆 Powerlevel10k 仓库，打开终端，输入以下命令：
```git clone --depth=1 https://gitee.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k```
配置 Zsh 使用 Powerlevel10k 主题
```sudo nano ~/.zshrc```
```ZSH_THEME="powerlevel10k/powerlevel10k"```
使配置生效：
```source ~/.zshrc```
重启终端以配置：
```p10k configure```
#### 五、安装字体（推荐字体）
使用 Nerd Fonts 字体，下载以下 4 个 ttf 文件，双击每个文件，然后单击 “Install”。
  - [MesloLGS NF Regular.ttf](https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf)
  - [MesloLGS NF Bold.ttf](https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold.ttf)
  - [MesloLGS NF Italic.ttf](https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Italic.ttf)
  - [MesloLGS NF 粗体Italic.ttf](https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold%20Italic.ttf)
终端字体选择`MesloLGS NF`，enjoy it!