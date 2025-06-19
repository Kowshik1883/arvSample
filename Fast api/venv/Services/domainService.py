from Database.mongo import db

domain_db = db["domains"]
class DomainService:
    async def get_all_domains():
        domains = []
        async for doc in domain_db.find():
            domains.append({
                'id': str(doc.get('_id')),
                'DomainId': doc.get('DomainId'),
                'Name': doc.get('Name'),
                'Status': doc.get('Status'),
                'CreatedBy': doc.get('CreatedBy'),
                'CreatedAt': doc.get('CreatedAt')
            })
        return domains