import json
from typing import List, Type, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from app.services.firebase.firebase_service_exception import FirebaseServiceException
from app.services.firebase.firebase_service_interface import FirebaseServiceInterface
from app.services.firebase.firebase_object import FirebaseObject

# Firebase service implementation
class FirebaseService(FirebaseServiceInterface):
    def __init__(self, api_key: str):
        self.db = None
        self.__initialize(api_key=api_key)

    def __initialize(self, api_key: str):
        """
        Initialize Firebase Admin SDK with the service account key from the environment.
        """
        
        if not firebase_admin._apps:  # Check if Firebase app is already initialized
            # If you're using the raw JSON string, load it as a dictionary
            cred_dict = json.loads(api_key)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)

        # Initialize Firestore client
        self.db = firestore.client()

    def add(self, obj: FirebaseObject) -> str:
        """
        Add an object to the specified Firestore collection.
        
        :param obj: The dictionary object to be added to Firestore.
        :param collection_name: The name of the Firestore collection where the object should be added.
        :return: The document ID of the added object.
        """

        try:
            # Access the specified collection
            collection_ref = self.db.collection(obj.collection_name())
            # Add the object to Firestore
            _, doc_ref = collection_ref.add(obj.model_dump(exclude_unset=True))
            obj.id = doc_ref.id
            return obj  # Return the document with ID
        except Exception as e:
            # Raise a custom exception if there's an error
            raise FirebaseServiceException(f"Failed to add document to {obj.collection_name()}: {str(e)}")
        
    def add_with_doc_id(self, doc_id: str, obj: FirebaseObject) -> str:
        """
        Add an object to the specified Firestore collection with specific document ID.
        
        :param obj: The dictionary object to be added to Firestore.
        :param collection_name: The name of the Firestore collection where the object should be added.
        :return: The document ID of the added object.
        """

        try:
            # Access the specified collection
            collection_ref = self.db.collection(obj.collection_name()).document(doc_id)
            # Add the object with specific ID to Firestore
            collection_ref.set(obj.model_dump(exclude_unset=True))
            return obj  # Return the document
        except Exception as e:
            # Raise a custom exception if there's an error
            raise FirebaseServiceException(f"Failed to add document to {obj.collection_name()}: {str(e)}")
        
    def delete(self, collection_name: str, document_id: str):
        """
        Delete an object by its document ID from the specified Firestore collection.
        
        :param collection_name: The Firestore collection name where the document resides.
        :param document_id: The document ID of the object to delete.
        """
        try:
            # Access the specified collection
            collection_ref = self.db.collection(collection_name)

            # Get a reference to the document
            doc_ref = collection_ref.document(document_id)

            # Delete the document
            doc_ref.delete()
        except Exception as e:
            raise FirebaseServiceException(f"Failed to delete document: {str(e)}")
        
    def fetch_all(self, model_class: Type[FirebaseObject], filters: Optional[List[FieldFilter]] = None) -> List[FirebaseObject]:
        """
        Fetch all documents from a specified Firestore collection and convert them into objects of type `model_class`.

        :param collection_name: Name of the Firestore collection to fetch data from.
        :param model_class: The class to which the documents should be mapped (e.g., User, Product).
        :return: A list of objects of type `model_class`.
        """
        try:
            # Get all documents from the specified Firestore collection
            collection_ref = self.db.collection(model_class.collection_name())

            # Apply the filter if provided
            if filters:
                filtered = collection_ref
                for filter in filters:        
                    filtered = filtered.where(filter=filter)
                documents = filtered.stream()
            else:
                documents = collection_ref.stream()

            objects = []
            for doc in documents:
                # Convert Firestore document to model instance
                data = doc.to_dict()
                data["id"] = doc.id  # Include the document ID
                obj = model_class(**data)  # Create an instance of the model class using the data
                objects.append(obj)

            return objects

        except Exception as e:
            print(f"Error fetching documents from {model_class.collection_name()}: {str(e)}")
            raise Exception(f"Error fetching documents from {model_class.collection_name()}: {str(e)}")

    def fetch_by_id(self, model_class: Type[FirebaseObject], doc_id: str) -> FirebaseObject:
        """
        Fetch a single document from the specified Firestore collection by its ID
        and convert it into an object of the specified model class.
        
        :param collection_name: Name of the Firestore collection to fetch data from.
        :param doc_id: Document ID of the Firestore document to retrieve.
        :param model_class: The class to which the document should be mapped (e.g., User).
        :return: An object of type `model_class`.
        """
        try:
            # Access the document by ID
            doc_ref = self.db.collection(model_class.collection_name()).document(doc_id)
            doc = doc_ref.get()  # Get the document
            
            if not doc.exists:
                raise Exception(f"Document with ID {doc_id} not found.")

            # Convert the document data into an instance of the model_class
            data = doc.to_dict()
            data["id"] = doc.id  # Include the Firestore document ID in the data
            
            # Create the model instance from the data
            return model_class(**data)  # Convert to the model (e.g., User)
        except Exception as e:
            raise Exception(f"Error fetching document from {model_class.collection_name()}: {str(e)}")
        

    def update(self, id: str, obj: FirebaseObject) -> FirebaseObject:
        """
        Update an existing document in the specified Firestore collection by its ID.
        
        :param collection_name: Name of the Firestore collection.
        :param doc_id: The ID of the document to update.
        :param obj: The object to update the document with (should be a Pydantic model).
        :return: The document ID of the updated object.
        """
        try:
            # Get document reference by ID
            doc_ref = self.db.collection(obj.collection_name()).document(id)

            # Convert the Pydantic model to a dictionary
            data = obj.model_dump(exclude_unset=True)  # Exclude unset fields

            # Update the document in Firestore
            doc_ref.set(data, merge=True)  # merge=True will update only the fields provided, not the entire document

            data["id"] = id
            return data  # Return the document ID of the updated object

        except Exception as e:
            raise Exception(f"Error updating document with ID {id}: {str(e)}")
        
    def add_to_subcollection(
        self,
        parent_collection: Type[FirebaseObject],
        parent_id: str,
        obj: FirebaseObject
    ) -> str:
        """
        Добавляет объект obj в подколлекцию obj.collection_name()
        документа parent_collection/parent_id и возвращает ID созданного документа.
        """
        try:
            parent_ref = self.db.collection(parent_collection.collection_name()).document(parent_id)
            subcol_ref = parent_ref.collection(obj.collection_name())
            _, doc_ref = subcol_ref.add(obj.model_dump(exclude_unset=True))
            return doc_ref.id
        except Exception as e:
            raise FirebaseServiceException(
                f"Adding subcollection failure {obj.collection_name()} "
                f"document {parent_collection.collection_name()}/{parent_id}: {e}"
            )
        
    def close_db(self):
        """
        Close the Firestore database connection.
        """
        self.db.close()

    