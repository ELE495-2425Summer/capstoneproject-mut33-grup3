# TOBB ETÜ ELE495 - Capstone Project

# Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Acknowledgements](#acknowledgements)

## Introduction
Provide a brief overview of the project, its purpose, and what problem it aims to solve.

#EN
The vehicle will send natural language voice commands received from the user to an artificial intelligence model (LLM). This will analyze the commands, translate them into basic driving commands, and execute these commands using sensors.

Furthermore, the vehicle will provide the user with vocal feedback, similar to natural Turkish speech (as non-robotic as possible), as the vehicle executes the commands.

The operating scenario can be briefly summarized as follows: The user gives a series of commands in natural Turkish (e.g., "Go straight until you encounter an obstacle, then turn left, go forward for 2 seconds, turn right"). The vehicle's onboard microprocessor records the voice command and transcribes it using a voice recognition service. The transcribed command is analyzed using an artificial intelligence model (LLM) and converted into basic movement commands. The resulting commands are executed sequentially. The vehicle performs the assigned tasks through its motors and sensors. During the execution, the vehicle will provide users with vocal feedback in Turkish (e.g., "I'm currently driving forward," "I'm turning left").

#TR
Araç kullanıcıdan alınan doğal dil şeklindeki sesli komutları bir yapay zeka modeline (LLM) göndererek komutları analiz edecek, temel sürüş komutlarına çevirecek ve bu komutları sensör destekli olarak uygulayacaktır.

Ayrıca araç komutları yerine getirirken kullanıcıya Türkçe doğal konuşma benzeri (mümkün olduğunca robotik olmayan bir şekilde) sesli geribildirim verecektir. 

Çalışma senaryosu kısaca şöyle özetlenebilir: Kullanıcı Türkçe olarak doğal konuşma diliyle bir dizi komut verir (örneğin: “engel çıkana kadar düz git, sonra sola dön, 2 saniye ileri git, sağa dön”). Araç üzerindeki mikroişlemci/mikrobilgisayar sesli komutu kaydeder ve bir ses tanıma servisi üzerinden yazıya çevirir. Yazıya çevrilen komut, bir yapay zeka modeli (LLM) kullanılarak analiz edilir ve temel hareket komutlarına dönüştürülür. Elde edilen temel komutlar sırayla uygulanır. Araç motorları ve sensörler aracılığıyla verilen görevleri gerçekleştirir. Araç, uygulama esnasında kullanıcılara Türkçe olarak sesli olarak geribildirim verir ("şu anda ileri gidiyorum", "sola dönüyorum" gibi). 


## Features
List the key features and functionalities of the project.
- Hardware: The hardware components used (should be listed with links)
- Operating System and packages
- Applications 
- Services 

## Installation
Describe the steps required to install and set up the project. Include any prerequisites, dependencies, and commands needed to get the project running.

```bash
# Example commands
git clone https://github.com/username/project-name.git
cd project-name
```

## Usage
Provide instructions and examples on how to use the project. Include code snippets or screenshots where applicable.

## Screenshots
Include screenshots of the project in action to give a visual representation of its functionality. You can also add videos of running project to YouTube and give a reference to it here. 

## Acknowledgements
Give credit to those who have contributed to the project or provided inspiration. Include links to any resources or tools used in the project.

[Contributor 1](https://github.com/user1)
[Resource or Tool](https://www.nvidia.com)
