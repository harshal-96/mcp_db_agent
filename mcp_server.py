# mcp_legal_server.py
from mcp.server.fastmcp import FastMCP
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import argparse
from typing import List, Dict, Optional

# Ensure database tables are created
models.Base.metadata.create_all(bind=engine)

mcp = FastMCP("LegalDB", port=3000)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here as we need to return the session

@mcp.tool()
def get_all_cases() -> List[Dict]:
    """Gets all cases from the legal database.
    
    Returns:
        List[Dict]: List of all cases with their details including client and lawyer information.
    """
    db = get_db()
    try:
        cases = db.query(models.Case).all()
        result = []
        for case in cases:
            case_data = {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "client_id": case.client_id,
                "lawyer_id": case.lawyer_id,
                "created_at": str(case.created_at) if hasattr(case, 'created_at') else None
            }
            
            # Add client information if available
            if case.client:
                case_data["client_name"] = case.client.name
                case_data["client_contact"] = case.client.contact
            
            # Add lawyer information if available
            if case.lawyer:
                case_data["lawyer_name"] = case.lawyer.name
                case_data["lawyer_specialization"] = case.lawyer.specialization
                
            result.append(case_data)
        return result
    finally:
        db.close()

@mcp.tool()
def get_case_by_id(case_id: int) -> Dict:
    """Gets a specific case by its ID.
    
    Args:
        case_id: The ID of the case to retrieve.
        
    Returns:
        Dict: Case information with client and lawyer details.
        
    Raises:
        ValueError: If case with given ID is not found.
    """
    db = get_db()
    try:
        case = db.query(models.Case).filter(models.Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case with ID {case_id} not found")
            
        case_data = {
            "id": case.id,
            "title": case.title,
            "description": case.description,
            "client_id": case.client_id,
            "lawyer_id": case.lawyer_id,
            "created_at": str(case.created_at) if hasattr(case, 'created_at') else None
        }
        
        # Add client information if available
        if case.client:
            case_data["client_name"] = case.client.name
            case_data["client_contact"] = case.client.contact
        
        # Add lawyer information if available
        if case.lawyer:
            case_data["lawyer_name"] = case.lawyer.name
            case_data["lawyer_specialization"] = case.lawyer.specialization
            
        return case_data
    finally:
        db.close()

@mcp.tool()
def add_case(title: str, description: str, client_id: int, lawyer_id: int) -> Dict:
    """Adds a new case to the legal database.
    
    Args:
        title: The title of the case.
        description: The description of the case.
        client_id: The ID of the client associated with the case.
        lawyer_id: The ID of the lawyer assigned to the case.
        
    Returns:
        Dict: The created case information.
        
    Raises:
        ValueError: If client or lawyer with given IDs don't exist.
    """
    db = get_db()
    try:
        # Verify client exists
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
            
        # Verify lawyer exists
        lawyer = db.query(models.Lawyer).filter(models.Lawyer.id == lawyer_id).first()
        if not lawyer:
            raise ValueError(f"Lawyer with ID {lawyer_id} not found")
        
        case = models.Case(
            title=title,
            description=description,
            client_id=client_id,
            lawyer_id=lawyer_id
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        
        return {
            "id": case.id,
            "title": case.title,
            "description": case.description,
            "client_id": case.client_id,
            "lawyer_id": case.lawyer_id,
            "client_name": client.name,
            "lawyer_name": lawyer.name,
            "message": "Case added successfully"
        }
    finally:
        db.close()

@mcp.tool()
def get_all_clients() -> List[Dict]:
    """Gets all clients from the legal database.
    
    Returns:
        List[Dict]: List of all clients with their information.
    """
    db = get_db()
    try:
        clients = db.query(models.Client).all()
        return [
            {
                "id": client.id,
                "name": client.name,
                "contact": client.contact
            }
            for client in clients
        ]
    finally:
        db.close()

@mcp.tool()
def get_client_by_id(client_id: int) -> Dict:
    """Gets a specific client by their ID.
    
    Args:
        client_id: The ID of the client to retrieve.
        
    Returns:
        Dict: Client information.
        
    Raises:
        ValueError: If client with given ID is not found.
    """
    db = get_db()
    try:
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
            
        return {
            "id": client.id,
            "name": client.name,
            "contact": client.contact
        }
    finally:
        db.close()

@mcp.tool()
def add_client(name: str, contact: str) -> Dict:
    """Adds a new client to the legal database.
    
    Args:
        name: The name of the client.
        contact: The contact information of the client.
        
    Returns:
        Dict: The created client information.
    """
    db = get_db()
    try:
        client = models.Client(name=name, contact=contact)
        db.add(client)
        db.commit()
        db.refresh(client)
        
        return {
            "id": client.id,
            "name": client.name,
            "contact": client.contact,
            "message": "Client added successfully"
        }
    finally:
        db.close()

@mcp.tool()
def get_all_lawyers() -> List[Dict]:
    """Gets all lawyers from the legal database.
    
    Returns:
        List[Dict]: List of all lawyers with their information.
    """
    db = get_db()
    try:
        lawyers = db.query(models.Lawyer).all()
        return [
            {
                "id": lawyer.id,
                "name": lawyer.name,
                "specialization": lawyer.specialization
            }
            for lawyer in lawyers
        ]
    finally:
        db.close()

@mcp.tool()
def get_lawyer_by_id(lawyer_id: int) -> Dict:
    """Gets a specific lawyer by their ID.
    
    Args:
        lawyer_id: The ID of the lawyer to retrieve.
        
    Returns:
        Dict: Lawyer information.
        
    Raises:
        ValueError: If lawyer with given ID is not found.
    """
    db = get_db()
    try:
        lawyer = db.query(models.Lawyer).filter(models.Lawyer.id == lawyer_id).first()
        if not lawyer:
            raise ValueError(f"Lawyer with ID {lawyer_id} not found")
            
        return {
            "id": lawyer.id,
            "name": lawyer.name,
            "specialization": lawyer.specialization
        }
    finally:
        db.close()

@mcp.tool()
def add_lawyer(name: str, specialization: str) -> Dict:
    """Adds a new lawyer to the legal database.
    
    Args:
        name: The name of the lawyer.
        specialization: The specialization area of the lawyer.
        
    Returns:
        Dict: The created lawyer information.
    """
    db = get_db()
    try:
        lawyer = models.Lawyer(name=name, specialization=specialization)
        db.add(lawyer)
        db.commit()
        db.refresh(lawyer)
        
        return {
            "id": lawyer.id,
            "name": lawyer.name,
            "specialization": lawyer.specialization,
            "message": "Lawyer added successfully"
        }
    finally:
        db.close()

@mcp.tool()
def get_cases_by_client(client_id: int) -> List[Dict]:
    """Gets all cases associated with a specific client.
    
    Args:
        client_id: The ID of the client.
        
    Returns:
        List[Dict]: List of cases for the specified client.
        
    Raises:
        ValueError: If client with given ID is not found.
    """
    db = get_db()
    try:
        # Verify client exists
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
            
        cases = db.query(models.Case).filter(models.Case.client_id == client_id).all()
        result = []
        for case in cases:
            case_data = {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "client_id": case.client_id,
                "lawyer_id": case.lawyer_id,
                "client_name": client.name
            }
            
            # Add lawyer information if available
            if case.lawyer:
                case_data["lawyer_name"] = case.lawyer.name
                case_data["lawyer_specialization"] = case.lawyer.specialization
                
            result.append(case_data)
        return result
    finally:
        db.close()

@mcp.tool()
def get_cases_by_lawyer(lawyer_id: int) -> List[Dict]:
    """Gets all cases assigned to a specific lawyer.
    
    Args:
        lawyer_id: The ID of the lawyer.
        
    Returns:
        List[Dict]: List of cases for the specified lawyer.
        
    Raises:
        ValueError: If lawyer with given ID is not found.
    """
    db = get_db()
    try:
        # Verify lawyer exists
        lawyer = db.query(models.Lawyer).filter(models.Lawyer.id == lawyer_id).first()
        if not lawyer:
            raise ValueError(f"Lawyer with ID {lawyer_id} not found")
            
        cases = db.query(models.Case).filter(models.Case.lawyer_id == lawyer_id).all()
        result = []
        for case in cases:
            case_data = {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "client_id": case.client_id,
                "lawyer_id": case.lawyer_id,
                "lawyer_name": lawyer.name
            }
            
            # Add client information if available
            if case.client:
                case_data["client_name"] = case.client.name
                case_data["client_contact"] = case.client.contact
                
            result.append(case_data)
        return result
    finally:
        db.close()

@mcp.tool()
def search_cases(query: str) -> List[Dict]:
    """Searches for cases by title or description.
    
    Args:
        query: The search query to match against case titles and descriptions.
        
    Returns:
        List[Dict]: List of cases matching the search query.
    """
    db = get_db()
    try:
        cases = db.query(models.Case).filter(
            (models.Case.title.contains(query)) | 
            (models.Case.description.contains(query))
        ).all()
        
        result = []
        for case in cases:
            case_data = {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "client_id": case.client_id,
                "lawyer_id": case.lawyer_id
            }
            
            # Add client information if available
            if case.client:
                case_data["client_name"] = case.client.name
                case_data["client_contact"] = case.client.contact
            
            # Add lawyer information if available
            if case.lawyer:
                case_data["lawyer_name"] = case.lawyer.name
                case_data["lawyer_specialization"] = case.lawyer.specialization
                
            result.append(case_data)
        return result
    finally:
        db.close()

if __name__ == "__main__":
    # Start the server
    print("🚀 Starting Legal Database MCP Server...")

    # Debug Mode
    # uv run mcp dev mcp_legal_server.py

    # Production Mode
    # uv run mcp_legal_server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )
    
    args = parser.parse_args()
    print("Server type:", args.server_type)
    print("Launching on Port:", 3000)
    print('Check "http://localhost:3000/sse" for the server status')
    
    mcp.run(args.server_type)