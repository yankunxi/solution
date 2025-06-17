# solution
last update: 2025-06-22_16:46:03

`We want a model that generates images to prompts like “Yankun hiking in a mountain” , “Yankun in an office”, “Yankun skiing”`

This is doable in ComfyUI and I have it ready on my own server. I didn't catch up with the latest release but it should be enough.

```
### ComfyUI Version: v0.3.9-9-g601ff9e | Released on '2024-12-21'
** Python version: 3.12.8 | packaged by Anaconda, Inc. | (main, Dec 11 2024, 16:31:09) [GCC 11.2.0]
Total VRAM 24111 MB, total RAM 31297 MB
pytorch version: 2.5.1+cu124
Set vram state to: NORMAL_VRAM
Device: cuda:0 NVIDIA GeForce RTX 4090 : cudaMallocAsync
Using pytorch attention
```

* I'll start from SDXL-Lightning as the basic sampler, which is fast with minor loss of image quality, to build the workflow.
    * If we need to replace with a better once if we need to improve the performance.

* We start from a basic workflow that can generate image with full set of prompts.
    * The resolution is set to be 1024 *  768. A community modified version for realistic photos of SDXL-Lightning is applied.
* To make it easier for tracking, Width, Height, Seed and Positive Prompt are isolated in the workflow to form an input zone.     
    * Some parameters that are not often changed and conrolling the image style or quality such as negative promt, sampler steps/methods are left in the nodes.

![workflow](https://github.com/user-attachments/assets/b923c688-fd7d-4691-89c8-784bde7be1f6)

* It's working now. But the human part relies too much on the description and has nothing from a specific person.
    * The best way to solve is is obviously using a reference from the person.
    * The most convenient way would be a single photo from cell phone camera. Of course, providing more details would be nice.
    * There were several method and community built addons that can do this.
        * I was using face swapping in my previous project, but it was more time consuming and performance wasn't perfect.
        * I started with InstantID and also tried IP-Adapter(Face/Full), T2I-Adapter
        * However, InstantID seems to provide the best performance
            * Here I use a photo of mine from 6 month ago, since when I lose 18 lbs and had haircut recently.
            * I also set the batch size to 4 for better testing speed.

![workflow_1](https://github.com/user-attachments/assets/85ac1a22-3533-4d99-9008-d80cd5653586)

* It looks good. But the pose and direction is limitted without a pose reference in this setting.
    * A straight-forward solution is to generate a reference. So I reused some parts of the workflow to generate less polished images just for pose reference.
    * This workflow structure is chosen after many adjusts and has a balance of simplism and performance.
    * Of course, there are options to keep the original pose or use controlnet to generate images in specific poses easily.
    * I changed the descriptional promt from "35 years old asian" to just "a person", so you can see the pose reference photo has large diversity. The performance is still good and there are some added flavors.
* There are low chances to generate a bad reference image (for example the person is too far from the camera, or facing back to the cameral), in this case the generator will automatically use another image in the batch as reference, which is good.
    * To be honest, some of the images are prettly like my real photos.

![workflow_2](https://github.com/user-attachments/assets/fc64a5bc-84b7-4803-9f2d-6fc109a57f83)

* Then I test it for other inputs such as "in the office". The prompt "portrait" is somehow too close for the photos, and other words cannot control camera distance good enough either, so I decide to adjust the reference image size to generate the photo in a good distance.
    * The distance can be conditional or even infered from the input prompt if needed.
    * The quality is pretty close to or even better than some of the existing "profesional profile" boothing apps.

![workflow_3](https://github.com/user-attachments/assets/d63bfd41-ac6a-43ae-90fb-48f5680d3cea)

* Then I finalize this simple workflow to make it easier for input. One can just input an activity (or with locations) and a photo to use it. It can be done from the frontend/backbend, but it has some advantages to be done in the workflow.
* There are lots of aspects that can be improved upon requests.
    * If user wants to provide more photos, there are more available techniques such as face embedding. Also, a specific name can be used to awake the embedding.
    * Classification can be added after the image generation to ensure output quality as well as NFW content filter.
    * S

![workflow_f](https://github.com/user-attachments/assets/b928e1ee-0d2e-42ad-a55d-31a4b6d2049d)

* I'll try to host the server publicly for 1-2 days as a consideration of network safety (I didn't purchase a professional reverse proxy service so authorized connection is very limited). Or there probably are some cloud hoster for ComfyUI but I'm not sure.
* The server addresss is [https://localserver.voguediffusion.ai/](https://localserver.voguediffusion.ai/)
    * It should be all English but probably contains some Chinese.
* To use the workflow, you can just right click and download the latest workflow png 574314869267336.png, then drag it into the comfyUI webpage, then the workflow should be loaded. You can scoll up and down to zoom, drag blank to move the canvas, change the prompt, upload an image or choose existing images for input. Click the blue start button to generate a batch of 4 images to test.
* It takes about 5 hours to solve this problem and write down everything, and one more hour to set up the server/github.
