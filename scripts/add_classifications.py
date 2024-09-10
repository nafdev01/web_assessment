import json
from django.core.exceptions import ObjectDoesNotExist
from assessment.models import Classification, ClassificationReference

def run():
    try:
        # Load the JSON data
        with open("classifications.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: The file 'classifications.json' was not found.")
        return
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from 'classifications.json'.")
        return

    for classification_name, classification_data in data.items():
        try:
            # Create or get the Classification object
            classification, created = Classification.objects.get_or_create(
                name=classification_name,
                defaults={
                    'description': classification_data.get("desc", ""),
                    'solution': classification_data.get("sol", ""),
                }
            )
            if created:
                print(f"Created classification: {classification_name}")
            else:
                print(f"Classification already exists: {classification_name}")

            # Add or update ClassificationReference objects
            for reference_name, reference_link in classification_data.get("ref", {}).items():
                ClassificationReference.objects.get_or_create(
                    classification=classification,
                    name=reference_name,
                    defaults={'reference_link': reference_link}
                )
        except Exception as e:
            print(f"Error processing classification '{classification_name}': {e}")

# Ensure this script is run within a Django context (e.g., using Django management commands)
if __name__ == "__main__":
    run()
