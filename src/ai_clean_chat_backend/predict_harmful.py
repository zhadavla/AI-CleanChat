from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np

# Load the tokenizer and model once outside the function
model_directory = "src/ai_clean_chat_backend/trained_model"
tokenizer_deser = BertTokenizer.from_pretrained(model_directory)
model_deser = BertForSequenceClassification.from_pretrained(model_directory)

# Set the model to evaluation mode once
model_deser.eval()


def predict_harmfulness(texts):
    """
    Function to predict the class of given texts.

    Args:
    texts (list of str): List of input texts to classify.

    Returns:
    list of str: Predicted labels ('hate_speech', 'offensive_language', or 'neither') for each text.
    """
    # Tokenize all the input texts at once (batch tokenization)
    inputs = tokenizer_deser(texts, return_tensors='pt', truncation=True, padding=True, max_length=32)

    # Run the model on the batch of inputs to get outputs
    outputs = model_deser(**inputs)

    # Extract logits (raw model predictions)
    logits = outputs.logits

    # Convert logits to probabilities and get the predicted class index for each input text
    predicted_classes = np.argmax(logits.detach().numpy(), axis=1)

    # Map the class index to the actual label
    label_map = {0: 'hate_speech', 1: 'offensive_language', 2: 'neither'}

    # Return the predicted labels
    return [label_map[pred] for pred in predicted_classes]
