from flask import request
from flask_restx import Namespace, Resource, fields
from Utils.Response import success_response, error_response
from database import db
from models import Client

client_routes = Namespace("client", description="Client management API")

client_create_model = client_routes.model(
    "ClientCreate",
    {
        "name": fields.String(required=True, description="Client full name"),
        "email": fields.String(required=False, description="Client email address"),
        "phone": fields.String(required=True, description="Client phone number"),
        "address": fields.String(required=False, description="Street address"),
        "city": fields.String(required=False, description="City"),
        "state": fields.String(required=False, description="State / Region"),
        "pincode": fields.String(required=False, description="Postal / Pin code"),
        "company_name": fields.String(required=False, description="Company or business name"),
        "gst_number": fields.String(required=False, description="GST or tax identification number"),
        "status": fields.String(required=False, default="active", description="Status (active/inactive)"),
    }
)

client_update_model = client_routes.model(
    "ClientUpdate",
    {
        "name": fields.String(required=False, description="Client full name"),
        "email": fields.String(required=False, description="Client email address"),
        "phone": fields.String(required=False, description="Client phone number"),
        "address": fields.String(required=False, description="Street address"),
        "city": fields.String(required=False, description="City"),
        "state": fields.String(required=False, description="State / Region"),
        "pincode": fields.String(required=False, description="Postal / Pin code"),
        "company_name": fields.String(required=False, description="Company or business name"),
        "gst_number": fields.String(required=False, description="GST or tax identification number"),
        "status": fields.String(required=False, description="Status (active/inactive)"),
    }
)


def serialize_client(client):
    """Helper to convert Client SQLAlchemy model into a clean JSON-ready dictionary"""
    return {
        "id": client.id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "address": client.address,
        "city": client.city,
        "state": client.state,
        "pincode": client.pincode,
        "company_name": client.company_name,
        "gst_number": client.gst_number,
        "status": client.status if client.status else "active",
        "created_at": client.created_at.isoformat() if client.created_at else None,
        "updated_at": client.updated_at.isoformat() if client.updated_at else None,
    }


# ----------------------------------------------------------------------
# 1. CREATE CLIENT
# ----------------------------------------------------------------------
@client_routes.route("/create_client")
class ClientCreate(Resource):

    @client_routes.expect(client_create_model)
    def post(self):
        try:
            data = request.get_json()

            if not data:
                return error_response(message="Please provide client details", status_code=400)

            name = data.get("name", "").strip() if data.get("name") else ""
            phone = data.get("phone", "").strip() if data.get("phone") else ""

            if not name:
                return error_response(message="Client name is required", status_code=400)
            if not phone:
                return error_response(message="Client phone number is required", status_code=400)

            # Clean optional email and check uniqueness
            raw_email = data.get("email")
            email = raw_email.strip() if (raw_email and raw_email.strip()) else None
            if email:
                existing_email = Client.query.filter(Client.email == email).first()
                if existing_email:
                    return error_response(message=f"Client with email '{email}' already exists", status_code=409)

            # Clean optional GST and check uniqueness
            raw_gst = data.get("gst_number")
            gst_number = raw_gst.strip() if (raw_gst and raw_gst.strip()) else None
            if gst_number:
                existing_gst = Client.query.filter(Client.gst_number == gst_number).first()
                if existing_gst:
                    return error_response(message=f"Client with GST '{gst_number}' already exists", status_code=409)

            new_client = Client(
                name=name,
                email=email,
                phone=phone,
                address=data.get("address", "").strip() if data.get("address") else None,
                city=data.get("city", "").strip() if data.get("city") else None,
                state=data.get("state", "").strip() if data.get("state") else None,
                pincode=data.get("pincode", "").strip() if data.get("pincode") else None,
                company_name=data.get("company_name", "").strip() if data.get("company_name") else None,
                gst_number=gst_number,
                status=data.get("status", "active") if data.get("status") else "active",
            )

            db.session.add(new_client)
            db.session.commit()

            return success_response(
                message="Client added successfully",
                data=serialize_client(new_client),
                status_code=201
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))


# ----------------------------------------------------------------------
# 2. READ ALL CLIENTS
# ----------------------------------------------------------------------
@client_routes.route("/read_client")
class ClientList(Resource):
    def get(self):
        try:
            clients = Client.query.order_by(Client.id.desc()).all()

            result = [serialize_client(c) for c in clients]
            return success_response(
                message="Clients retrieved successfully",
                data=result
            )

        except Exception as e:
            return error_response(str(e))


# ----------------------------------------------------------------------
# 3. READ SINGLE CLIENT
# ----------------------------------------------------------------------
@client_routes.route("/read_client/<int:id>")
class ClientDetail(Resource):
    @client_routes.param("id", "Client ID", _in="path", required=True)
    def get(self, id):
        try:
            client = db.session.get(Client, id)
            if not client:
                return error_response(
                    message="Client not found",
                    status_code=404
                )

            return success_response(
                message="Client details retrieved successfully",
                data=serialize_client(client)
            )
        except Exception as e:
            return error_response(str(e))


# ----------------------------------------------------------------------
# 4. UPDATE CLIENT INFO (NEW ROUTE)
# ----------------------------------------------------------------------
@client_routes.route("/update_client/<int:id>")
class ClientUpdate(Resource):

    @client_routes.expect(client_update_model)
    @client_routes.param("id", "Client ID to update", _in="path", required=True)
    def put(self, id):
        try:
            client = db.session.get(Client, id)
            if not client:
                return error_response(
                    message="Client not found",
                    status_code=404
                )

            data = request.get_json()
            if not data:
                return error_response(message="No update data provided", status_code=400)

            # Update Name
            if "name" in data:
                name_val = data["name"].strip() if data["name"] else ""
                if not name_val:
                    return error_response(message="Client name cannot be empty", status_code=400)
                client.name = name_val

            # Update Phone
            if "phone" in data:
                phone_val = data["phone"].strip() if data["phone"] else ""
                if not phone_val:
                    return error_response(message="Client phone cannot be empty", status_code=400)
                client.phone = phone_val

            # Update Email with duplicate check
            if "email" in data:
                new_email = data["email"].strip() if (data["email"] and data["email"].strip()) else None
                if new_email:
                    existing_email = Client.query.filter(Client.email == new_email, Client.id != id).first()
                    if existing_email:
                        return error_response(
                            message=f"Email '{new_email}' is already registered to another client",
                            status_code=409
                        )
                client.email = new_email

            # Update GST with duplicate check
            if "gst_number" in data:
                new_gst = data["gst_number"].strip() if (data["gst_number"] and data["gst_number"].strip()) else None
                if new_gst:
                    existing_gst = Client.query.filter(Client.gst_number == new_gst, Client.id != id).first()
                    if existing_gst:
                        return error_response(
                            message=f"GST number '{new_gst}' is already assigned to another client",
                            status_code=409
                        )
                client.gst_number = new_gst

            # Update Optional Fields
            if "address" in data:
                client.address = data["address"].strip() if data["address"] else None
            if "city" in data:
                client.city = data["city"].strip() if data["city"] else None
            if "state" in data:
                client.state = data["state"].strip() if data["state"] else None
            if "pincode" in data:
                client.pincode = data["pincode"].strip() if data["pincode"] else None
            if "company_name" in data:
                client.company_name = data["company_name"].strip() if data["company_name"] else None
            if "status" in data and data["status"]:
                client.status = data["status"].strip()

            db.session.commit()

            return success_response(
                message="Client information updated successfully",
                data=serialize_client(client)
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e))

    # Also support PATCH for partial updates
    @client_routes.expect(client_update_model)
    @client_routes.param("id", "Client ID to update", _in="path", required=True)
    def patch(self, id):
        return self.put(id)


# ----------------------------------------------------------------------
# 5. DELETE CLIENT
# ----------------------------------------------------------------------
@client_routes.route("/delete_client/<int:id>")
class ClientDelete(Resource):

    @client_routes.param("id", "Client ID", _in="path", required=True)
    def delete(self, id):
        try:
            client = db.session.get(Client, id)
            if not client:
                return error_response(
                    message="Client not found",
                    status_code=404
                )

            client_name = client.name
            db.session.delete(client)
            db.session.commit()

            return success_response(
                message=f"Client '{client_name}' removed successfully",
                data={"deleted_client_id": id}
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))


# ----------------------------------------------------------------------
# 6. SEARCH CLIENTS
# ----------------------------------------------------------------------
@client_routes.route("/search_client")
class ClientSearch(Resource):

    @client_routes.doc(params={"name": "Client name, phone, company, or email keyword"})
    def get(self):
        try:
            query = request.args.get("name", "").strip()
            if not query:
                return error_response("Search query parameter 'name' is required", 400)

            search_pattern = f"%{query}%"
            stmt = db.select(Client).filter(
                (Client.name.ilike(search_pattern)) |
                (Client.company_name.ilike(search_pattern)) |
                (Client.phone.ilike(search_pattern)) |
                (Client.email.ilike(search_pattern)) |
                (Client.city.ilike(search_pattern))
            )

            result = db.session.execute(stmt).scalars().all()

            output = [serialize_client(item) for item in result]

            return success_response(
                message=f"Found {len(output)} client(s) matching '{query}'",
                data=output
            )

        except Exception as e:
            return error_response(str(e))
   