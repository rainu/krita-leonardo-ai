# Krita Plugin for the Leonardo.Ai

[Leonardo.AI](https://leonardo.ai) is an awesome service for generating and manipulating 
Images with AI. They provide an own Web-Application for generating and manipulating images
with AI. However, their Web-Application is not (yet) a full-featured painting tool!

Therefore, I decided to develop a plugin which connects the power of Leonardo.AI with the
open source and powerful painting application [Krita](https://krita.org)

# Setup
1. Clone or copy the plugin into the krita-plugin directory (see [Krita - Manually](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html#manually))
2. Copy the desktop-file to krita-plugin directory
3. (Re-)Start krita
4. Enable Plugin (see [Krita - How to enable and disable a plugin?](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html#how-to-enable-and-disable-a-plugin))
5. Add "Leonardo AI" docker (see [Krita - How to get to the plugin?](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html#how-to-enable-and-disable-a-plugin))

## Linux

```shell
cd ~/.local/share/krita/pykrita
git clone https://github.com/rainu/krita-leonardo-ai.git leonardo_ai
ln -s ./leonardo_ai/leonardo_ai.desktop
```

## Windows

1. Download the latest [leonardo_ai.zip](https://github.com/rainu/krita-leonardo-ai/releases)
2. Unpack the whole content into the Krita-Plugin Directory
```
C:\Users\YOUR_USERNAME\AppData\Roaming\krita\pykrita
```

# Settings

Of course, you will need a Leonardo AI-Account first. After you have some you can configure your credentials in the 
Plugin's Settings. If the plugin is loaded without configured credentials, the settings dialog should be automatically 
open. There you can put your credentials and check if the connection is possible. After save your settings, you are
read to work with the plugin!
