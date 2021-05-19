# Yesprit
This is a tool that design primers for four fission yeast species.

Please select the corresponding version according to your operating platform.

The compiled executable files for Windows, MacOS, and Linux are available here (https://github.com/Sugiyama-Lab/Yesprit/releases).

## Compile from source code

We use [PyInstaller](https://www.pyinstaller.org/) to compile our Python application into stand-alone executable.

```{bash}
pip install pyinstaller # and also other dependensies that Yesprit requires but not installed on users' local
pyinstaller cli.spec
```

## Run without compilation

We modulelized the script so that users with basic Python knowledge can run the application directly with our source code.  

```{bash}
# Clone and install
git clone https://github.com/Sugiyama-Lab/Yesprit.git
cd Yesprit
python setup.py install
# Run
Yesprit
```
