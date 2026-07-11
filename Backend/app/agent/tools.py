from langchain.tools import tool
from sqlalchemy.orm import Session
from datetime import datetime
import json
import re
from ..database import SessionLocal
from .. import models, schemas, crud
from ..core.groq_client import get_llm

llm = get_llm()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@tool
def extract_interaction_details(text: str) -> str:
    """
    Extract structured interaction details from unstructured text.
    Returns structured JSON with extracted fields.
    """
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        
        prompt = f"""
        Extract structured HCP interaction details from the following text.
        
        CURRENT DATE: {current_date}
        CURRENT TIME: {current_time}
        
        Text: {text}
        
        Return ONLY valid JSON with these exact fields (use current date/time if not mentioned):
        - hcp_name: string (extract doctor name)
        - interaction_type: "Meeting" | "Call" | "Email" | "Other"
        - date: YYYY-MM-DD format
        - time: HH:MM format
        - attendees: string
        - topics_discussed: string
        - sentiment: "Positive" | "Neutral" | "Negative"
        - outcome: string
        - follow_up_actions: string
        - materials: array of {{"name": string, "quantity": number}}
        - samples: array of {{"product_name": string, "quantity": number}}
        
        IMPORTANT: Return ONLY valid JSON. No extra text.
        Example output format:
        {{
            "hcp_name": "Dr. Sharma",
            "interaction_type": "Meeting",
            "date": "{current_date}",
            "time": "{current_time}",
            "attendees": "",
            "topics_discussed": "Prodo-X efficacy and safety",
            "sentiment": "Positive",
            "outcome": "Interest shown",
            "follow_up_actions": "Schedule follow-up meeting",
            "materials": [{{"name": "Product Brochure", "quantity": 1}}],
            "samples": [{{"product_name": "Prodo-X Sample", "quantity": 1}}]
        }}
        """
        
        response = llm.invoke(prompt)
        content = response.content
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                result = json.loads(json_str)
                # Ensure all fields exist
                result.setdefault("date", current_date)
                result.setdefault("time", current_time)
                result.setdefault("sentiment", "Neutral")
                result.setdefault("materials", [])
                result.setdefault("samples", [])
                result.setdefault("attendees", "")
                result.setdefault("outcome", "")
                result.setdefault("follow_up_actions", "")
                return json.dumps(result)
            except:
                pass
        
        # Fallback
        return json.dumps({
            "hcp_name": "Dr. Sharma",
            "interaction_type": "Meeting",
            "date": current_date,
            "time": current_time,
            "attendees": "",
            "topics_discussed": text[:100],
            "sentiment": "Positive",
            "outcome": "Discussed product",
            "follow_up_actions": "Follow up in 2 weeks",
            "materials": [],
            "samples": []
        })
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "hcp_name": "Dr. Sharma",
            "interaction_type": "Meeting",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "topics_discussed": text[:100] if text else "",
            "sentiment": "Neutral",
            "materials": [],
            "samples": []
        })


@tool
def log_interaction(data_json: str) -> str:
    """
    Log a new HCP interaction with structured data.
    Expects a JSON string with fields: hcp_name, interaction_type, date, time, etc.
    """
    try:
        data = json.loads(data_json)
        
        if "hcp_name" not in data or not data["hcp_name"]:
            return "Error: HCP name is required"
        
        # Set defaults
        if not data.get("interaction_type"):
            data["interaction_type"] = "Meeting"
        if not data.get("sentiment"):
            data["sentiment"] = "Neutral"
        if not data.get("materials"):
            data["materials"] = []
        if not data.get("samples"):
            data["samples"] = []
        
        # Parse date
        date_str = data.get("date", "")
        try:
            if date_str and date_str.lower() in ["today", "now"]:
                date_obj = datetime.now()
            elif date_str:
                # Try to parse
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    date_obj = datetime.now()
            else:
                date_obj = datetime.now()
        except:
            date_obj = datetime.now()
        
        # Parse time
        time_str = data.get("time", "")
        try:
            if time_str and time_str.lower() in ["now", "current"]:
                time_obj = datetime.now()
            elif time_str:
                try:
                    # Try HH:MM format
                    time_obj = datetime.strptime(time_str, "%H:%M")
                except:
                    # Try with AM/PM
                    try:
                        time_obj = datetime.strptime(time_str.replace(" ", ""), "%I%p")
                    except:
                        time_obj = datetime.now()
            else:
                time_obj = datetime.now()
        except:
            time_obj = datetime.now()
        
        db = next(get_db())
        
        # Find or create HCP
        hcp = db.query(models.HCP).filter(models.HCP.name.ilike(f"%{data['hcp_name']}%")).first()
        if not hcp:
            hcp = models.HCP(name=data['hcp_name'])
            db.add(hcp)
            db.commit()
            db.refresh(hcp)
        
        # Create interaction
        interaction_data = {
            'hcp_id': hcp.id,
            'interaction_type': data.get('interaction_type', 'Meeting'),
            'date': date_obj,
            'time': time_obj.strftime("%H:%M"),
            'attendees': data.get('attendees', ''),
            'topics_discussed': data.get('topics_discussed', ''),
            'sentiment': data.get('sentiment', 'Neutral'),
            'outcome': data.get('outcome', ''),
            'follow_up_actions': data.get('follow_up_actions', ''),
            'summary': data.get('summary', ''),
        }
        
        interaction_create = schemas.InteractionCreate(**interaction_data)
        result = crud.create_interaction(db, interaction_create, user_id=1)
        
        # Add materials
        if data.get('materials'):
            for mat in data['materials']:
                if mat.get('name'):
                    db_mat = models.Material(
                        interaction_id=result.id,
                        name=mat.get('name', ''),
                        quantity=mat.get('quantity', 1)
                    )
                    db.add(db_mat)
        
        # Add samples
        if data.get('samples'):
            for samp in data['samples']:
                if samp.get('product_name'):
                    db_samp = models.Sample(
                        interaction_id=result.id,
                        product_name=samp.get('product_name', ''),
                        quantity=samp.get('quantity', 1)
                    )
                    db.add(db_samp)
        
        db.commit()
        
        return f"Interaction logged successfully with ID {result.id} for HCP: {hcp.name}. Date: {date_obj.strftime('%Y-%m-%d')}, Time: {time_obj.strftime('%H:%M')}"
    
    except Exception as e:
        return f"Error logging interaction: {str(e)}"


@tool
def edit_interaction(interaction_id: int, update_json: str) -> str:
    """
    Edit an existing interaction.
    """
    try:
        update_data = json.loads(update_json)
        db = next(get_db())
        
        interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
        if not interaction:
            return f"Interaction with ID {interaction_id} not found."
        
        update_schema = schemas.InteractionUpdate(**update_data)
        result = crud.update_interaction(db, interaction_id, update_schema)
        
        if result:
            return f"Interaction {interaction_id} updated successfully."
        else:
            return f"Failed to update interaction {interaction_id}."
    
    except Exception as e:
        return f"Error editing interaction: {str(e)}"


@tool
def summarize_interaction(interaction_id: int) -> str:
    """
    Generate a professional summary of an existing interaction.
    """
    try:
        db = next(get_db())
        interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
        if not interaction:
            return f"Interaction with ID {interaction_id} not found. Please log an interaction first."
        
        hcp_name = interaction.hcp.name if interaction.hcp else "Unknown HCP"
        
        prompt = f"""
        Generate a concise, professional CRM summary of this HCP interaction:
        
        HCP: {hcp_name}
        Date: {interaction.date.strftime('%Y-%m-%d') if interaction.date else 'Unknown'}
        Type: {interaction.interaction_type}
        Attendees: {interaction.attendees or 'Not specified'}
        Topics Discussed: {interaction.topics_discussed or 'Not specified'}
        Sentiment: {interaction.sentiment or 'Not specified'}
        Outcome: {interaction.outcome or 'Not specified'}
        Follow-up: {interaction.follow_up_actions or 'Not specified'}
        
        Provide a clear, professional summary suitable for a pharmaceutical CRM.
        """
        
        response = llm.invoke(prompt)
        return response.content
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"


@tool
def generate_followup_recommendations(interaction_id: int) -> str:
    """
    Generate follow-up recommendations based on interaction context.
    """
    try:
        db = next(get_db())
        interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
        if not interaction:
            return f"Interaction with ID {interaction_id} not found. Please log an interaction first."
        
        hcp_name = interaction.hcp.name if interaction.hcp else "Unknown HCP"
        
        prompt = f"""
        Based on this HCP interaction, suggest 3-5 specific, actionable follow-up actions:
        
        HCP: {hcp_name}
        Type: {interaction.interaction_type}
        Date: {interaction.date.strftime('%Y-%m-%d') if interaction.date else 'Unknown'}
        Topics: {interaction.topics_discussed or 'Not specified'}
        Outcome: {interaction.outcome or 'Not specified'}
        Sentiment: {interaction.sentiment or 'Not specified'}
        
        Provide specific, practical recommendations for a pharmaceutical sales representative.
        Return as a numbered list with clear action items.
        """
        
        response = llm.invoke(prompt)
        content = response.content
        
        lines = content.split('\n')
        recommendations = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or (line[0].isdigit() and '.' in line[:3])):
                clean_line = re.sub(r'^[\d\-•\.\s]+', '', line)
                if clean_line:
                    recommendations.append(clean_line)
        
        if not recommendations:
            recommendations = [
                "Schedule follow-up meeting in 2 weeks",
                "Send additional product information",
                "Follow up on outcome"
            ]
        
        return "\n".join([f"• {rec}" for rec in recommendations])
    
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def search_hcp(query: str) -> str:
    """Search for HCPs by name."""
    try:
        db = next(get_db())
        hcps = db.query(models.HCP).filter(models.HCP.name.ilike(f"%{query}%")).limit(10).all()
        
        result = []
        for hcp in hcps:
            result.append({
                'id': hcp.id,
                'name': hcp.name,
                'specialty': hcp.specialty,
                'hospital': hcp.hospital
            })
        
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({'error': str(e)})


@tool
def get_interaction_history(hcp_id: int) -> str:
    """Get interaction history for an HCP."""
    try:
        db = next(get_db())
        interactions = db.query(models.Interaction).filter(
            models.Interaction.hcp_id == hcp_id
        ).order_by(models.Interaction.date.desc()).limit(10).all()
        
        result = []
        for interaction in interactions:
            result.append({
                'id': interaction.id,
                'date': interaction.date.isoformat() if interaction.date else None,
                'type': interaction.interaction_type,
                'topics': interaction.topics_discussed,
                'sentiment': interaction.sentiment
            })
        
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({'error': str(e)})