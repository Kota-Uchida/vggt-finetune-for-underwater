# README.md

## What does this repository for?
This repository is made for generating synthesized underwater scene data with Infinigen, and directory use it for the finetuning of VGGT. Further extension to training other models will be updated.

## How can I use this?
On the top directory, you will find 4 codes, ``manipulate_gin.py``,``implement_infinigen.sh``, ``preprocess_infinigen.py``, ``train_vggt.sh``. Unless you want to inspect the internal mechanism of these codes, all you need to manipulate is only these codes!

The whole process can be broken down into 4 steps.

### 1. Prepare gin file
Infinigen exploits numbers of gin files to manage the paremeters. There are several configurations you should always include, and one of them is "the camera configurations". In order to generate camera configuration file for your settings, you can use ``manipulate_gin.sh``. You can configure the setting by editing this bash script.

By default, this python script generate the configuration that align all the cameras on the same circle specified by the argument. Note that you can only apply 1-9 cameras, otherwise the output directory naming will fail.

### 2. Generate scene data with Infinigen
You can use ``implement_infinigen.sh`` to implement the infinigen scene generation. Inside the bash script is not complicated at all. Feel free to write your own configuration. However, be sure to leave the output directory inside ``infinigen/output/~`` because the later codes make such an assumption that all the data are stored under this directory.

### 3. Data preprocessing for vggt finetuning
To format the generated data, ``preprocess_infinigen.py`` will help you with this. All you need to do is to implement this code with some arguments. Following is an example:

```
python preprocess_infingen.py --infinigen_data_dir infinigen/outputs/coral_0 infinigen/outputs/coral_1 --data_output_dir vggt/dataset --annotation_output_dir vggt/annotations --category coral --train_split 0.8 --seed 42
```
If you are keeping the directory tree as it is, you can use ``preprocess_infinigen.sh``.


### 4. Implement finetuning of VGGT
Now you are ready to train VGGT. There are several demo code to try using vggt on your own data. ``demo_viser.sh`` does forward pass of the image data and you can see the reconstructed 3d scene on viser. ``demo_colmap.sh`` does forward pass, and it produces estimated depth and pointcloud data in the colmap format.

### 5. Train VGGT on Infinigen data
``train_vggt.sh`` will do this job. In order to configure on which data you want to train, and several other hyperparameter settings, you need to edit ``vggt/training/config/default_config.yaml``.