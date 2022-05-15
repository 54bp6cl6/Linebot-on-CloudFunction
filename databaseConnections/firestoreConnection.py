from google.cloud import firestore

class FirestoreConnection:
    def __init__(self) -> None:
        self.db = firestore.Client()

    def getUserInfo(self, user_id: str) -> dict:
        doc_snapshot = self.db.collection(u'UserInfo').document(user_id).get()
        return doc_snapshot.to_dict() if doc_snapshot.exists else None

    def setUserInfo(self, user_id: str, user_info: dict) -> None:
        doc = self.db.collection(u'UserInfo').document(user_id)
        if doc.get().exists:
            doc.update(user_info)
        else:
            doc.create(user_info)
        

    def close(self) -> None:
        self.db.close()