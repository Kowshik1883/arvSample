from Database.mongo import db

domain_db = db["domains"]
class DomainService:
    async def get_all_domains():
        domains = []
        async for doc in domain_db.find():
            domains.append({
                'DomainId': doc.get('DomainId'),
                'Name': doc.get('Name')
            })
        return domains