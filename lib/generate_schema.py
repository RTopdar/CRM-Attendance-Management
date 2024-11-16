import pandas as pd
import json


def generate_worker_schema(df: pd.DataFrame, output_file: str) -> None:
    """
    Generate a JSON schema for the given dataframe and save it to the output file.

    Args:
    df (pd.DataFrame): Input dataframe
    output_file (str): Output file path

    Returns:
    None
    """
    schema = {"bsonType": "object", "required": [], "properties": {}}

    for _, row in df.iterrows():
        field_name = row["VARIABLE NAME"]
        data_type = row["DATA TYPE"]
        description = row["DESCRIPTION"]

        # Determine bsonType
        bson_type = "string"  # Default to string if not specified
        if isinstance(data_type, str):
            if data_type.lower() == "objectid":
                bson_type = "objectId"
            elif data_type.lower() == "array":
                bson_type = "array"
            elif data_type.lower() == "string":
                bson_type = "string"
            elif data_type.lower() == "number":
                bson_type = "double"
            elif data_type.lower() == "email":
                bson_type = "string"
                schema["properties"][field_name][
                    "pattern"
                ] = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            # Add more type mappings as needed

        schema["properties"][field_name] = {
            "bsonType": bson_type,
            "description": description,
        }

        if pd.notna(row["VALIDATION RULES"]):
            try:
                validation_rules = json.loads(row["VALIDATION RULES"])
                if isinstance(validation_rules, dict):
                    schema["properties"][field_name].update(validation_rules)
                else:
                    print(
                        f"Skipping invalid validation rules for field '{field_name}': {row['VALIDATION RULES']}"
                    )
            except json.JSONDecodeError:
                print(
                    f"Skipping invalid JSON in validation rules for field '{field_name}': {row['VALIDATION RULES']}"
                )

        if field_name == "STATUS":
            schema["properties"][field_name]["enum"] = [
                "Available",
                "Absent",
                "Assigned",
            ]

        if pd.notna(row["COMMENT"]) and "required" in row["COMMENT"].lower():
            schema["required"].append(field_name)

    with open(output_file, "w") as f:
        json.dump(schema, f, indent=4)


def create_client_schema():
    csv_file_path = "schema/Attendance Schema - Client.csv"
    df = pd.read_csv(csv_file_path)
    
    schema = {"bsonType": "object", "required": [], "properties": {}}

    for _, row in df.iterrows():
        field_name = row["VARIABLE NAME"]
        data_type = row["DATA TYPE"]
        description = row["DESCRIPTION"]

        # Determine bsonType
        bson_type = "string"  # Default to string if not specified
        if isinstance(data_type, str):
            if data_type.lower() == "objectid":
                bson_type = "objectId"
            elif data_type.lower() == "array":
                bson_type = "array"
            elif data_type.lower() == "string":
                bson_type = "string"
            elif data_type.lower() == "number":
                bson_type = "double"
            elif data_type.lower() == "date":
                bson_type = "date"
            elif data_type.lower() == "email":
                bson_type = "string"
                schema["properties"][field_name] = {
                    "bsonType": bson_type,
                    "description": description,
                    "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"
                }
                continue

        schema["properties"][field_name] = {
            "bsonType": bson_type,
            "description": description,
        }

        if pd.notna(row["VALIDATION RULES"]):
            try:
                validation_rules = json.loads(row["VALIDATION RULES"])
                if isinstance(validation_rules, dict):
                    schema["properties"][field_name].update(validation_rules)
                else:
                    print(
                        f"Skipping invalid validation rules for field '{field_name}': {row['VALIDATION RULES']}"
                    )
            except json.JSONDecodeError:
                print(
                    f"Skipping invalid JSON in validation rules for field '{field_name}': {row['VALIDATION RULES']}"
                )

        if pd.notna(row["COMMENT"]) and "required" in row["COMMENT"].lower():
            schema["required"].append(field_name)

    output_file = "schema/client_schema.json"
    with open(output_file, "w") as f:
        json.dump(schema, f, indent=4)

if __name__ == "__main__":
    # csv_file_path = "schema/Attendance Schema - Workers.csv"
    # output_file = "schema/attendance_schema.json"
    # df = pd.read_csv(csv_file_path)
    # generate_schema(df, output_file)
    create_client_schema()
