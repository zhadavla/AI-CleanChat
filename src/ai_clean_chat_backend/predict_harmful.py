import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Load the tokenizer and model once outside the function
model_directory = "src/ai_clean_chat_backend/trained_model"
tokenizer_deser = BertTokenizer.from_pretrained(model_directory)
model_deser = BertForSequenceClassification.from_pretrained(model_directory)

# Set the device once (GPU if available, otherwise CPU)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Move the model to the device and set it to evaluation mode once
# model_deser.to(device)
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
    inputs = tokenizer_deser(texts, return_tensors='pt', truncation=True, padding='max_length', max_length=32)

    # Move inputs to the same device as the model
    # inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        # Run the model on the batch of inputs to get outputs
        outputs = model_deser(**inputs)

    # Extract logits (raw model predictions)
    logits = outputs.logits

    # Get the predicted class index for each input text (argmax across the class dimension)
    predicted_classes = torch.argmax(logits, dim=1).cpu().numpy()

    # Map the class index to the actual label
    label_map = {0: 'hate_speech', 1: 'offensive_language', 2: 'neither'}

    # Return the predicted labels
    return [label_map[pred] for pred in predicted_classes]


