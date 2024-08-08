# -*- coding: utf-8 -*-
"""Poison Ivy Detection V2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K80-YXlgyY36B2oUVVz8dRFCuiP2sooJ

## **Importing necessary classes**
"""

import os
import cv2
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from skimage.feature import hog
from sklearn.naive_bayes import GaussianNB
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from google.colab import drive

"""## **Obtaining Dataset**"""

from google.colab import drive
drive.mount('/content/drive/')

# Path to the dataset
dataset_path = '/content/drive/MyDrive/Machine Learning Project - Poison Ivy Detection/data_all'

"""## **Preprocessing**"""

# Function to load images from the directory - CNN
def load_images_from_folder(folder):
    images = []
    labels = []
    for filename in os.listdir(folder):
        label = folder.split('/')[-1]
        img = cv2.imread(os.path.join(folder, filename))
        if img is not None:
            img = cv2.resize(img, (128, 128))
            images.append(img)
            labels.append(label)
    return images, labels
# Function to load images from the directory and apply HOG - LOG REG, Naive Bayes, SVM
def load_images_from_folder_and_extract_hog(folder):
    images = []
    labels = []
    for filename in os.listdir(folder):
        label = folder.split('/')[-1]
        img = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            img = cv2.resize(img, (128, 128))
            hog_features = hog(img, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True)
            images.append(hog_features)
            labels.append(label)
    return images, labels

# Loading poison ivy images and labels for LOG REG, Naive Bayes, SVM
poison_ivy_images, poison_ivy_labels = load_images_from_folder_and_extract_hog(os.path.join(dataset_path, 'poison_ivy'))

# Loading poison ivy images and labels for LOG REG, Naive Bayes, SVM
raspberry_images, raspberry_labels = load_images_from_folder_and_extract_hog(os.path.join(dataset_path, 'raspberry'))

# Combine the image datasets
images = poison_ivy_images + raspberry_images
# Combine the label data
labels = poison_ivy_labels + raspberry_labels

# Convert to numpy arrays
images = np.array(images)
labels = np.array(labels)

# Label Encoding
le = LabelEncoder()
# Fit Transform Labels
labels = le.fit_transform(labels)

# 80%/20% Training/Test Split
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

# Flattening Images for LOG REG, Naive Bayes, SVM
X_train_flattened = X_train.reshape(X_train.shape[0], -1)
X_test_flattened = X_test.reshape(X_test.shape[0], -1)

"""## **Model 1 - Logistic Regression**"""

# Logistic Regression
log_Reg = LogisticRegression(max_iter=1000)
log_Reg.fit(X_train_flattened, y_train)
log_Reg_pred = log_Reg.predict(X_test_flattened)

"""## **Model 2 - Naive Bayes**"""

# Gaussian Naive Bayes
nb = GaussianNB()
nb.fit(X_train, y_train)
nb_pred = nb.predict(X_test)

"""## **Model 3 - SVM**"""

# SVM
svm = SVC(kernel='linear')
svm.fit(X_train_flattened, y_train)
svm_pred = svm.predict(X_test_flattened)

"""## **Model 4 - CNN**"""

### Preprocessing for CNN

# Loading poison ivy images and labels for LOG REG, Naive Bayes, SVM
poison_ivy_images, poison_ivy_labels = load_images_from_folder(os.path.join(dataset_path, 'poison_ivy'))

# Loading poison ivy images and labels for LOG REG, Naive Bayes, SVM
raspberry_images, raspberry_labels = load_images_from_folder(os.path.join(dataset_path, 'raspberry'))

# Combine the image datasets
images = poison_ivy_images + raspberry_images
# Combine the label data
labels = poison_ivy_labels + raspberry_labels

# Convert to numpy arrays
images = np.array(images)
labels = np.array(labels)

# Label Encoding
le = LabelEncoder()
# Fit Transform Labels
labels = le.fit_transform(labels)

# 80%/20% Training/Test Split
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

# Loading the Dataset class
class PlantDataset(Dataset):
    def __init__(self, images, labels, transform=None):
        self.images = images
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

# Ensure that images are correctly formatted as tensors before fed into model
transform = transforms.Compose([
    transforms.ToPILImage(), # Converts tensor to PIL Image
    transforms.ToTensor(), # Converts PIL Image to tensor
])

# Setting dataset using class
training_dataset = PlantDataset(X_train, y_train, transform=transform)
test_dataset = PlantDataset(X_test, y_test, transform=transform)

# Loading dataset
training_loader = DataLoader(training_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)


# Convolutional Neural Network Class
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1) # 1st convolution Layer
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2) # Filter
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1) # 2nd convolution Layer
        self.fc1 = nn.Linear(64 * 32 * 32, 128) # Fully Connected Layer
        self.fc2 = nn.Linear(128, 2) # Output layer

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 32 * 32)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Initializing model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNN()

learning_rate = 0.001

# Cross entropy loss
criterion = nn.CrossEntropyLoss()
# adam optimizer
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Initalzing arrays to store losses and accuracies
train_losses = []
val_losses = []
val_accuracies = []

# Training Section
num_epochs = 50
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, labels in training_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    # Storing Training Losses
    train_losses.append(running_loss/len(training_loader))

    # Validation Section
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    # Storing Validation Losses and accuracies
    val_losses.append(val_loss/len(test_loader))
    val_accuracies.append(correct / total)

    print(f'Epoch {epoch+1}/{num_epochs}, Train Loss: {running_loss/len(training_loader)}, Val Loss: {val_loss/len(test_loader)}, Val Accuracy: {correct/total}')

# Plotting losses
plt.figure(figsize=(16, 6))
plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Validation Loss')
plt.title('Loss over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# Plotting accuracies
plt.subplot(1, 2, 2)
plt.plot(val_accuracies, label='Validation Accuracy')
plt.title('Validation Accuracy over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.show()

"""## **Results**"""

# Evaluating Logistic Regression
print("Logistic Regression:")
print("Accuracy:", accuracy_score(y_test, log_Reg_pred))
print("Precision:", precision_score(y_test, log_Reg_pred))
print("Recall:", recall_score(y_test, log_Reg_pred))
print("F1 Score:", f1_score(y_test, log_Reg_pred))

# Evaluating Naive Bayes
print("\nNaive Bayes:")
print("Accuracy:", accuracy_score(y_test, nb_pred))
print("Precision:", precision_score(y_test, nb_pred))
print("Recall:", recall_score(y_test, nb_pred))
print("F1 Score:", f1_score(y_test, nb_pred))

# Evaluating SVM
print("\nSVM:")
print("Accuracy:", accuracy_score(y_test, svm_pred))
print("Precision:", precision_score(y_test, svm_pred))
print("Recall:", recall_score(y_test, svm_pred))
print("F1 Score:", f1_score(y_test, svm_pred))

# Evaluating CNN
model.eval()
cnn_y_pred = []
cnn_y_true = []

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        cnn_y_pred.extend(predicted.cpu().numpy())
        cnn_y_true.extend(labels.cpu().numpy())

print("\nCNN:")
print("Accuracy:", accuracy_score(cnn_y_true, cnn_y_pred))
print("Precision:", precision_score(cnn_y_true, cnn_y_pred))
print("Recall:", recall_score(cnn_y_true, cnn_y_pred))
print("F1 Score:", f1_score(cnn_y_true, cnn_y_pred))

"""## **Confusion Matrices**"""

def plot_confusion_matrix(cm, title):
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='seismic', xticklabels=le.classes_, yticklabels=le.classes_)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title(title)
    plt.show()

# Confusion matrices
confMat_log_reg = confusion_matrix(y_test, log_Reg_pred)
confMat_nb = confusion_matrix(y_test, nb_pred)
confMat_svm = confusion_matrix(y_test, svm_pred)
confMat_cnn = confusion_matrix(cnn_y_true, cnn_y_pred)

# Plotting confusion matrices
plot_confusion_matrix(confMat_log_reg, "Logistic Regression Confusion Matrix")
plot_confusion_matrix(confMat_nb, "Gaussian Naive Bayes Confusion Matrix")
plot_confusion_matrix(confMat_svm, "SVM Confusion Matrix")
plot_confusion_matrix(confMat_cnn, "CNN Confusion Matrix")

"""### **Pretraining Models** - What if we pretrained our dataset with VGG16, a model used for image recognition that has over a million images?

## **Model 5 - CNN pretrained with VGG16**
"""

from torchvision import transforms, models

# Loading VGG16 Model
vgg16 = models.vgg16(pretrained=True)

# Freezing all the layers
for param in vgg16.parameters():
    param.requires_grad = False

# Replace the classifier part
vgg16.classifier[6] = nn.Linear(4096, 2)

# Initalizing Model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vgg16 = vgg16.to(device)

# Cross entropy loss
criterion = nn.CrossEntropyLoss()
# adam optimizer
optimizer = optim.Adam(vgg16.classifier[6].parameters(), lr=0.001)

# Initializing arrays to store losses and accuracies
train_losses = []
val_losses = []
train_accuracies = []
val_accuracies = []

# Training Section
num_epochs = 50
for epoch in range(num_epochs):
    vgg16.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for images, labels in training_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = vgg16(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    train_losses.append(running_loss/len(training_loader))
    train_accuracies.append(correct / total)

    # Validation
    vgg16.eval()
    val_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = vgg16(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    val_losses.append(val_loss/len(test_loader))
    val_accuracies.append(correct / total)

    print(f'Epoch {epoch+1}/{num_epochs}, Train Loss: {running_loss/len(training_loader)}, Train Accuracy: {correct/total}, Val Loss: {val_loss/len(test_loader)}, Val Accuracy: {correct/total}')

# Plotting losses
plt.figure(figsize=(16, 6))
plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Val Loss')
plt.title('Loss over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()


# Plotting accuracy
plt.subplot(1, 2, 2)
plt.plot(train_accuracies, label='Train Accuracy')
plt.plot(val_accuracies, label='Val Accuracy')
plt.title('Accuracy over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()


plt.show()

"""## **Evaluate**"""

# Evaluate CNN
vgg16.eval()
cnn_y_pred = []
cnn_y_true = []
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = vgg16(images)
        _, predicted = torch.max(outputs, 1)
        cnn_y_pred.extend(predicted.cpu().numpy())
        cnn_y_true.extend(labels.cpu().numpy())

print("CNN:")
print("Accuracy:", accuracy_score(cnn_y_true, cnn_y_pred))
print("Precision:", precision_score(cnn_y_true, cnn_y_pred))
print("Recall:", recall_score(cnn_y_true, cnn_y_pred))
print("F1 Score:", f1_score(cnn_y_true, cnn_y_pred))

"""## **Confusion Matrix**"""

# Confusion matrix
confMat_cnn = confusion_matrix(cnn_y_true, cnn_y_pred)

# Plotting confusion matrix
plot_confusion_matrix(confMat_cnn, "Pretrained CNN Confusion Matrix")

"""### **Demo**"""

from PIL import Image
import cv2
import numpy as np

def predict_image(image_path, model, le):
    # Read the image
    img = cv2.imread(image_path)

    # Check if the image was loaded correctly
    if img is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")

    # Convert image to grayscale if model was trained on grayscale images
    # Comment out this line if your model expects RGB images
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize the image to 90x90 pixels
    img = cv2.resize(img, (90, 90))

    # Normalize the image if needed (assuming the model expects values in [0, 1])
    img = img.astype('float32') / 255.0

    # Flatten the image to 2D array
    img = img.reshape(1, -1)  # -1 infers the remaining dimension

    # Print the shape of the image to debug the feature size
    print(f"Image shape for prediction: {img.shape}")

    # Make the prediction
    prediction = model.predict(img)

    # Transform the prediction to the class label
    predicted_class = le.inverse_transform(prediction)[0]

    return predicted_class

# Example usage
image_path = 'path to dataset'  # Replace with the path to your image
img = cv2.imread(image_path)
plt.imshow(img)
plt.title("TEST IMAGE")
plt.axis('off')
plt.show()


plt.show()

#Linear regression
result = predict_image(image_path, log_Reg, le)
print(f'\nThe image is classified as: {result}')

#Naive Bayes
result2 = predict_image(image_path, nb, le)
print(f'\nThe image is classified as: {result2}')

#SVM
result3 = predict_image(image_path, svm, le)
print(f'\nThe image is classified as: {result3}')

#CNN
#result4 = predict_image(image_path, model, le)
#print(f'\nThe image is classified as: {result4}')

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image

def predict_image_pytorch(image_path, mode, le):
    # Define image transformations
    transform = transforms.Compose([
        transforms.Resize((128, 128)),  # Resize to the input size expected by the CNN
        transforms.ToTensor(),  # Convert to a PyTorch tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize as per pretrained models
    ])

    # Open image and apply transformations
    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0)  # Add batch dimension

    # Print the shape of the image to debug the feature size
    print(f"Image shape for prediction: {img.shape}")

    # Make the prediction
    mode.eval()  # Set model to evaluation mode
    with torch.no_grad():
        prediction = mode(img)

    # Convert the prediction to the class label
    predicted_class = le.inverse_transform([torch.argmax(prediction, dim=1).item()])[0]

    return predicted_class

# Example usage
image_path = '/content/drive/MyDrive/Machine Learning Project - Poison Ivy Detection/raspberry/IMG_4430.jpg'  # Replace with the path to your image

# Assuming cnn_model is your trained PyTorch model and le is your LabelEncoder
result4 = predict_image_pytorch(image_path, model, le)
print(f'\nThe image is classified as: {result4}')