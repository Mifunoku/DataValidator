from google.cloud import firestore

db = firestore.Client()

def save_row(dataset_id, row_id, data):
    db.collection('datasets').document(dataset_id).collection('rows').document(str(row_id)).set(data)

def get_rows(dataset_id):
    rows_ref = db.collection('datasets').document(dataset_id).collection('rows')
    docs = rows_ref.stream()
    return [doc.to_dict() for doc in docs]

def update_row(dataset_id, row_id, fixed_category):
    row_ref = db.collection('datasets').document(dataset_id).collection('rows').document(str(row_id))
    row_ref.update({'fixed_category': fixed_category})
