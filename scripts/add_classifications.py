from assessment.models import Classification, ClassificationReference
import json


def run():
    # Load the JSON data
    with open("classifications.json", "r") as f:
        data = json.load(f)

    # Iterate over the data and create new Classification and ClassificationReference objects
    for classification_name, classification_data in data.items():
        classification, created = Classification.objects.get_or_create(
            name=classification_name,
            description=classification_data["desc"],
            solution=classification_data["sol"],
        )
        print(f"Created classification: {classification_name}")
        classification.save()

        for reference_name, reference_link in classification_data["ref"].items():
            ClassificationReference.objects.create(
                classification=classification,
                name=reference_name,
                reference_link=reference_link,
            )
            classification.save()
