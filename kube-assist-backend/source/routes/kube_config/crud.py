from source.database.models import CloudCreds
from uuid import UUID, uuid4
from source.database.database import get_db
from sqlalchemy import exists, and_

def add_cloudcreds_entry(userID: UUID, projectID: UUID, userKey: bytes, userValue: bytes, userRegion: bytes, clusterName: bytes):
    new_cloud_creds = CloudCreds(
        id = uuid4(),
        user_id=userID,
        project_id=projectID,
        key=userKey,
        value=userValue,
        region=userRegion,
        cluster_name=clusterName
    )

    with get_db() as db:
        db.add(new_cloud_creds)
        db.commit()

def is_cloudcreds_entry_exist(userID: UUID, projectID: UUID) -> bool:
    with get_db() as db:
        return db.query(
            exists().where(
                and_(
                    CloudCreds.user_id==userID,
                    CloudCreds.project_id==projectID
                )
            )
        ).scalar()
    
def get_cloudcreds(userID: UUID, projectID: UUID):
    with get_db() as db:
        cloud_creds = ( db.query(CloudCreds).with_entities(CloudCreds.key, CloudCreds.value, CloudCreds.region, CloudCreds.cluster_name).filter(CloudCreds.user_id==userID, CloudCreds.project_id==projectID).first() )

    return {"key": cloud_creds.key.decode('utf-8'), "value": cloud_creds.value.decode('utf-8'), "region": cloud_creds.region.decode('utf-8'), "name": cloud_creds.cluster_name.decode('utf-8')}
