import matplotlib.pyplot as plt
import numpy as np
import math
import csv


# Activation function that is used between the input and hidden layers
# 1. x is an array that represent the combined data from the input, weights and biases
def sigmoid(x: np.ndarray):
    value = 1.0 / (1.0 + np.exp(-x))
    return value


# Activation function that is used between the input and hidden layers (derivative version in the backward propagation)
# 1. x is an array that represent the combined data from the input, weights and biases
def sigmoid_derivative(x: np.ndarray):
    value = x * (1.0 - x)
    return value


# Activation function that returns the probability of the (mutually exclusive) classes, it is used at the output layer
# 1. x is an array that represent the combined data from the input, weights and biases
def softmax(x: np.ndarray):
    value = np.divide(np.exp(x), (sum([np.exp(i) for i in x])))
    return value


# Class that represent the artificial neural network
# 1. learning_rate is float that determine how quick the model adopts to the problem
# 2. layers is a list of integers that keep track on the input layer, hidden layers, and output layer
# 3. weights is a ndarray that influence the connections between neurons.
# 4. biases is a ndarray that influence the neuron internally.
class ArtificialNeuralNetwork:
    def __init__(self, layers: list[int], learning_rate: float):
        self.learning_rate = learning_rate
        self.layers = layers
        self.weights = []
        self.biases = []

        # Create the weights
        for i in range(0, len(layers) - 1):
            weight = np.random.standard_normal((layers[i + 1], layers[i]))
            self.weights.append(weight)

        # Create the biases
        for i in range(1, len(layers)):
            bias = np.zeros((layers[i], 1))
            self.biases.append(bias)

    # Function that feeds the errors back through the nural network to update the weights and biases
    # 1. sample is a list of floats that contains the normalized pixels values of a 28x28 image from the MINST dataset
    # 2. label is an integer value that is used to keep track of the correct class of sample
    # 3. outputs is a list of ndarrays that represent the output from the forward propagation
    def propagate_backward(self, sample: list[float], label: int, outputs: list[np.ndarray]):
        inputs = np.array(sample).reshape(self.layers[0], 1)
        errors = [[] for _ in outputs]

        # Calculate the errors
        for i in reversed(range(len(outputs))):
            output = outputs[i]
            next_layer = i + 1

            # Use softmax derivative at the output layer
            if i == len(outputs) - 1:
                correct_output = [1.0 if i == label else 0.0 for i in range(self.layers[-1])]
                correct_output = np.array(correct_output).reshape(self.layers[-1], 1)
                error = np.subtract(correct_output, output)
                errors[i] = error

            # Use sigmoid derivative at the other layers
            else:
                error = np.matmul(self.weights[next_layer].T, errors[next_layer])
                delta_error = np.multiply(error, sigmoid_derivative(output))
                errors[i] = delta_error

        # Update weights and biases
        for i in reversed(range(len(outputs))):
            if i == 0:
                input = inputs.reshape((self.layers[0], 1))
            else:
                input = outputs[i - 1]

            delta_weights = np.multiply(np.multiply(errors[i], input.T), self.learning_rate)
            self.weights[i] = np.add(self.weights[i], delta_weights)

            delta_biases = np.multiply(np.multiply(errors[i], 1), self.learning_rate)
            self.biases[i] = np.add(self.biases[i], delta_biases)

    # Function that feeds the sample forward through the nural network to calculate the probability of each class
    # 1. sample is a list of floats that contains the normalized pixels values of a 28x28 image from the MINST dataset
    def propagate_forward(self, sample: list[float]):
        inputs = np.array(sample).reshape(self.layers[0], 1)
        outputs = []

        for i in range(len(self.weights)):
            weight = self.weights[i]
            bias = self.biases[i]

            # Use softmax at the output layer
            if i == len(self.weights) - 1:
                inputs = softmax(np.matmul(weight, inputs) + bias)
                outputs.append(inputs)

            # Use sigmoid at the other layers
            else:
                inputs = sigmoid(np.matmul(weight, inputs) + bias)
                outputs.append(inputs)

        return outputs

    # Function that is used to validate the performance of the model
    # 1. samples is a list with other list filled with float values that represent the 28x28 images from the dataset
    # 2. labels is a list of integers that represent the correct classes of the samples
    def validate(self, samples: list[list[float]], labels: list[int]):
        correct_classifications = 0
        total_classifications = len(samples)
        correct_classifications_by_class = np.zeros(10)
        total_classifications_by_class = np.zeros(10)

        for i in range(len(samples)):
            sample = samples[i]
            label = labels[i]
            outputs = self.propagate_forward(sample)
            classification = np.argmax(outputs[-1])
            total_classifications_by_class[label] += 1
            if classification == label:
                correct_classifications += 1
                correct_classifications_by_class[classification] += 1

        percentage = correct_classifications / total_classifications * 100
        percentage_by_class = np.divide(correct_classifications_by_class, total_classifications_by_class) * 100
        return percentage, percentage_by_class

    # Function that trains the model (weight and biases) using backward propagation
    # 1. samples is a list with other list filled with float values that represent the 28x28 images from the dataset
    # 2. labels is a list of integers that represent the correct classes of the samples
    def training(self, samples: list[list[float]], labels: list[int]):
        correct_classifications = 0
        total_classifications = len(samples)

        for i in range(len(samples)):
            sample = samples[i]
            label = labels[i]
            outputs = self.propagate_forward(sample)
            classification = np.argmax(outputs[-1])
            if classification == label:
                correct_classifications += 1

            # "Learn from your mistakes"
            self.propagate_backward(sample, label, outputs)

        percentage = correct_classifications / total_classifications * 100
        return percentage


# Function that read the MINST dataset and it returns a training, validation, and testing subsets (samples and labels)
# 1. filename is a string that points out which file contains the dataset
# 2. percentage_training is a float value between 0 and 1 that determine the size of the training subset
# 3. percentage_validation is a float value between 0 and 1 that determine the size of the validation subset
# 4. percentage_testing is a float value between 0 and 1 that determine the size of the testing subset
def read_data_set(filename: str, percentage_training: float, percentage_validation: float, percentage_testing: float):
    x = []  # samples
    y = []  # labels
    with open(filename) as file:
        data = csv.reader(file)
        next(data)
        for row in data:
            y.append(int(row[0]))
            x.append([float(value) / 255 for value in row[1:]])

    # Create training, validation and testing subsets
    size_total = len(y)
    size_training = round(percentage_training * size_total)
    size_validation = round(percentage_validation * size_total)
    size_testing = round(percentage_testing * size_total)

    start = 0
    end = size_training
    x_training = x[start:end]
    y_training = y[start:end]

    start = size_training
    end = size_training + size_validation
    x_validation = x[start:end]
    y_validation = y[start:end]

    start = size_training + size_validation
    end = size_training + size_validation + size_testing
    x_testing = x[start:end]
    y_testing = y[start:end]

    return x_training, y_training, x_validation, y_validation, x_testing, y_testing


# Display the validation accuracy through the training process
def validation_accuracy_graph(accuracy: list):
    epochs = list(range(1, len(accuracy) + 1))
    plt.rcParams.update({'font.size': 16})
    plt.plot(epochs, accuracy, marker="o")
    plt.xlabel('Epochs')
    plt.ylabel('Training accuracy (%)')
    plt.title("Validation accuracy progress")
    plt.show()


# Display the testing accuracy by class
def testing_accuracy_by_class_graph(accuracy: list):
    names = [f"class '{i}'" for i in range(len(accuracy))]
    plt.bar(names, accuracy)
    plt.ylabel('Testing accuracy (%)')
    plt.title("Testing accuracy")
    low = min(accuracy)
    high = max(accuracy)
    plt.ylim([math.floor(low), math.ceil(high)])
    plt.show()


# Main code
if __name__ == "__main__":

    progress = []
    epochs = 20
    learning_rate = 0.08
    input_layer = 28 * 28
    output_layer = len([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    layers = [input_layer, 112, output_layer]
    ann = ArtificialNeuralNetwork(layers, learning_rate)
    x_training, y_training, x_validation, y_validation, x_testing, y_testing = read_data_set("data.csv", 0.7, 0.1, 0.2)

    for epoch in range(1, epochs + 1):
        accuracy_training = ann.training(x_training, y_training)
        accuracy_validation, accuracy_validation_by_class = ann.validate(x_validation, y_validation)
        print(f"Epoch {epoch} training accuracy......: {(accuracy_training):.2f}%")
        print(f"Epoch {epoch} validation accuracy....: {(accuracy_validation):.2f}%")
        progress.append(accuracy_validation)

    accuracy_testing, accuracy_testing_by_class = ann.validate(x_testing, y_testing)
    print(f"Testing accuracy..............: {(accuracy_testing):.2f}%")
    for i in range(len(accuracy_testing_by_class)):
        print(f"Testing accuracy for class '{i}'.: {(accuracy_testing_by_class[i]):.2f}%")

    print(f"Validation accuracy...........: {progress}")
    print(f"Testing accuracy..............: {accuracy_testing} ")
    print(f"Testing accuracy by class.....: {accuracy_testing_by_class}")
    print(f"Testing accuracy difference...: {(max(accuracy_testing_by_class) - min(accuracy_testing_by_class))}")

    validation_accuracy_graph(progress)
    testing_accuracy_by_class_graph(accuracy_testing_by_class)
