from flask import request
from flask_restx import Namespace, Resource, fields
from Utils.Response import success_response, error_response
from database import db
from models import Client

client_routes = Namespace("client", description = "Client management API")

client_create_model = client_routes.model(

    "ClientCreate",
    {
        "name" : fields.String(required=True, description="Client title"),
        "email" : fields.String(required=True, description="Client title"),
        "phone" : fields.String(required=True, description="Client title"),
        "address" : fields.String(required=True, description="Client title"),
        "city" : fields.String(required=True, description="Client title"),
        "state" : fields.String(required=True, description="Client title"),
        "pincode" : fields.String(required=True, description="Client title"),
        "company_name" : fields.String(required=True, description="Client title"),
        "gst_number" : fields.String(required=True, description="Client title"),
        "status" : fields.String(required=True, description="Client title"),
        
    }
    
)

@client_routes.route("/create_client")
class ClientListCreate(Resource):

    @client_routes.expect(client_create_model)
    def post(self):
        try:
            data = request.get_json()

            if not data :
                return error_response(message="Data Enter Kar")

            result = Client(
                name = data["name"],
                email = data["email"],
                phone = data["phone"],
                address = data["address"],
                city = data["city"],
                state = data["state"],
                pincode = data["pincode"],
                company_name= data["company_name"],
                gst_number = data["gst_number"],
                status = data["status"],
            )

            db.session.add(result)
            db.session.commit()

            return success_response(
            message="New Client Add",
            data={
                "id": result.id,
                "name": result.name,
                "email": result.email,
                "phone": result.phone,
                "address": result.address,
                "city": result.city,
                "state": result.state,
                "pincode": result.pincode,
                "company_name": result.company_name,
                "gst_number": result.gst_number,
                "status": result.status,
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None
            }
)
        except Exception as e:
            return error_response(str(e))

@client_routes.route("/read_client")
class ClientList(Resource):
    def get(self):
        try:
            data = Client.query.all()
            
            if not data:
                return error_response( 
                    message="Data Milat Nahi",
                    status_code=404
                )

            result = []
            for client in data:
                result.append({
                    "id": client.id,
                    "name": client.name,
                    "phone": client.phone,
                    "company_name":client.company_name
                })
            return success_response(
                message="Data Sapadala Ahe",
                data=result
            )

        except Exception as e:
            return error_response(e)