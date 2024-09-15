

# Define the predict_harmfulness function




# Main function to test predict_harmfulness
def main():
    # Test messages
    test_messages = [
        "I love this community!",
        "You are a terrible person.",
        "I hate everything about this.",
        "This is a friendly environment."
    ]

    # Check each message and display if it's harmful or not
    for message in test_messages:
        is_harmful = predict_harmfulness(message)
        if is_harmful:
            print(f"***HARMFUL***: {message}")
        else:
            print(f"Not harmful: {message}")


# Run the main function
if __name__ == "__main__":
    main()
