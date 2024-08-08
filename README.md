# ML_Final_Project
We used a github repository from another user containing 220 images of poison ivy leaves and 220 images of raspberry leaves. We then compared 4 machine learning
models' ability to correctly classify these images. The 4 models we used include: Linear regression, Gaussian Naive Bayes, SVM, and CNN. 

## 1. Datasets Used for Our Dataset:
  - https://github.com/bazilione/poison_ivy/blob/master/data_all.zip

## 2. Classical Models:
1. Logistic Regression: provided an 85.2% accuracy.
2. Naive Bayesian model: provided an 88.7% accuracy.
3. SVM: provided an 86.4% accuracy.
4. CNN: provided a 75% accuracy

## 3. How to run:
Once the dataset is downloaded to your Google Drive, this code is meant to be run in a linear fashion from top to bottom 
in order of how the cells are placed. Once all cells have been run, the demo cell can be run seperately to test a variety of images from the dataset.

In order to do this you have to import the dataset into your drive, then pull images from the drive into the code. Specifically the "_image_path_" function. Copy and paste the file path into this section and run. It will print out the test image, along side the result of what the model has predicted the image to be. 
