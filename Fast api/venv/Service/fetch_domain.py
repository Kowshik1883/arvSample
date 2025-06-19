from Database.mongo import domain_collection

def get_all_domains():
    domains=[]
    async for domain in domain_collection.find({"Status":"Active"}):
        domain["_id"]=str(domain["_id"])
        domains.append(domain)
    return domains