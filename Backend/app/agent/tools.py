from langchain.tools import tool
from sqlalchemy.orm import Session
from datetime import datetime
import json
import re
import logging
from ..database import SessionLocal
from .. import models, schemas, crud
from ..core.groq_client import get_llm

logger = logging.getLogger(__name__)
llm = get_llm()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@tool
def search_hcp(query: str) -> str:
    """
    Search for HCPs by name. Returns a JSON array of matching HCPs.
    Input: query - string containing HCP name to search for.
    """
    logger.info(f"🔍 search_hcp called with query: {query}")
    try:
        db = next(get_db())
        hcps = db.query(models.HCP).filter(models.HCP.name.ilike(f"%{query}%")).limit(10).all()
        
        result = []
        for hcp in hcps:
            result.append({
                'id': hcp.id,
                'name': hcp.name,
                'specialty': hcp.specialty,
                'hospital': hcp.hospital,
                'email': hcp.email,
                'phone': hcp.phone
            })
        
        logger.info(f"✅ search_hcp found {len(result)} results")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ search_hcp error: {str(e)}")
        return json.dumps({'error': str(e), 'results': []})


@tool
def get_interaction_history(hcp_id: int) -> str:
    """
    Get all interactions for a specific HCP by their numeric ID.
    Input: hcp_id - integer ID of the HCP.
    Returns JSON array of interactions.
    """
    logger.info(f"📋 get_interaction_history called with hcp_id: {hcp_id}")
    try:
        db = next(get_db())
        
        # Verify HCP exists
        hcp = db.query(models.HCP).filter(models.HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({'error': f'HCP with ID {hcp_id} not found', 'interactions': []})
        
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
                'sentiment': interaction.sentiment,
                'outcome': interaction.outcome,
                'follow_up_actions': interaction.follow_up_actions
            })
        
        logger.info(f"✅ get_interaction_history found {len(result)} interactions")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ get_interaction_history error: {str(e)}")
        return json.dumps({'error': str(e), 'interactions': []})


@tool
def extract_interaction_details(text: str) -> str:
    """Extract structured interaction details from unstructured text."""
    logger.info(f"📝 extract_interaction_details called with text length: {len(text)}")
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        
        prompt = f"""
        Extract structured HCP interaction details from the following text.
        
        CURRENT DATE: {current_date}
        CURRENT TIME: {current_time}
        
        Text: {text}
        
        Return ONLY valid JSON with these exact fields:
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
        """
        
        response = llm.invoke(prompt)
        content = response.content
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                result = json.loads(json_str)
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
        
        return json.dumps({
            "hcp_name": "Dr. Unknown",
            "interaction_type": "Meeting",
            "date": current_date,
            "time": current_time,
            "attendees": "",
            "topics_discussed": text[:100],
            "sentiment": "Neutral",
            "outcome": "",
            "follow_up_actions": "",
            "materials": [],
            "samples": []
        })
    except Exception as e:
        logger.error(f"❌ extract_interaction_details error: {str(e)}")
        return json.dumps({"error": str(e)})


@tool
def log_interaction(data_json: str) -> str:
    """Log a new HCP interaction with structured data."""
    logger.info(f"📝 log_interaction called with data length: {len(data_json)}")
    try:
        data = json.loads(data_json)
        
        if "hcp_name" not in data or not data["hcp_name"]:
            return "Error: HCP name is required"
        
        # Parse date
        date_str = data.get("date", "")
        try:
            if date_str and date_str.lower() in ["today", "now"]:
                date_obj = datetime.now()
            elif date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
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
                if "PM" in time_str or "AM" in time_str:
                    time_obj = datetime.strptime(time_str.replace(" ", ""), "%I%p")
                else:
                    time_obj = datetime.strptime(time_str, "%H:%M")
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
            logger.info(f"✅ Created new HCP: {hcp.name} (ID: {hcp.id})")
        else:
            logger.info(f"✅ Found existing HCP: {hcp.name} (ID: {hcp.id})")
        
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
        
        return f"Interaction logged successfully with ID {result.id} for HCP: {hcp.name} (ID: {hcp.id}). Date: {date_obj.strftime('%Y-%m-%d')}, Time: {time_obj.strftime('%H:%M')}"
    except Exception as e:
        logger.error(f"❌ log_interaction error: {str(e)}")
        return f"Error logging interaction: {str(e)}"


@tool
def edit_interaction(interaction_id: int, update_json: str) -> str:
    """Edit an existing interaction. Input: interaction_id (int) and update_json (string)."""
    logger.info(f"✏️ edit_interaction called with interaction_id: {interaction_id}")
    try:
        update_data = json.loads(update_json)
        db = next(get_db())
        
        interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
        if not interaction:
            return f"Interaction with ID {interaction_id} not found."
        
        update_schema = schemas.InteractionUpdate(**update_data)
        result = crud.update_interaction(db, interaction_id, update_schema)
        
        if result:
            logger.info(f"✅ Interaction {interaction_id} updated")
            return f"Interaction {interaction_id} updated successfully."
        else:
            return f"Failed to update interaction {interaction_id}."
    except Exception as e:
        logger.error(f"❌ edit_interaction error: {str(e)}")
        return f"Error editing interaction: {str(e)}"


@tool
def summarize_interaction(interaction_id: int) -> str:
    """
    Generate a professional summary of an existing interaction.
    Input: interaction_id - integer ID of the interaction to summarize.
    """
    logger.info(f"📋 summarize_interaction called with interaction_id: {interaction_id}")
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
        logger.info(f"✅ Summary generated for interaction {interaction_id}")
        return response.content
    except Exception as e:
        logger.error(f"❌ summarize_interaction error: {str(e)}")
        return f"Error generating summary: {str(e)}"


@tool
def generate_followup_recommendations(interaction_id: int) -> str:
    """
    Generate follow-up recommendations based on interaction context.
    Input: interaction_id - integer ID of the interaction to analyze.
    """
    logger.info(f"📋 generate_followup_recommendations called with interaction_id: {interaction_id}")
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
        
        # Parse recommendations
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
        
        logger.info(f"✅ Generated {len(recommendations)} follow-up recommendations")
        return "\n".join([f"• {rec}" for rec in recommendations])
    except Exception as e:
        logger.error(f"❌ generate_followup_recommendations error: {str(e)}")
        return f"Error generating recommendations: {str(e)}"