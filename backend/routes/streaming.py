from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import cv2
import numpy as np
from datetime import datetime

streaming_bp = Blueprint('streaming', __name__)

# Store active streaming sessions
active_streams = {}

@streaming_bp.route('/start', methods=['POST'])
@jwt_required()
def start_streaming():
    """Start a new streaming session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        language = data.get('language', 'ASL')
        quality = data.get('quality', 'medium')  # low, medium, high
        
        # Create streaming session
        session_id = f"stream_{user_id}_{datetime.now().timestamp()}"
        
        active_streams[session_id] = {
            'user_id': user_id,
            'language': language,
            'quality': quality,
            'started_at': datetime.now().isoformat(),
            'frame_count': 0,
            'translations': []
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'language': language,
            'quality': quality,
            'message': 'Streaming session started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/process_frame', methods=['POST'])
@jwt_required()
def process_frame():
    """Process a single video frame for sign language recognition"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        session_id = data.get('session_id')
        frame_data = data.get('frame')  # Base64 encoded frame
        timestamp = data.get('timestamp')
        
        if session_id not in active_streams:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        session = active_streams[session_id]
        
        # Decode frame
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        # Process frame with ML model (placeholder)
        translation_result = process_sign_language_frame(frame, session['language'])
        
        # Update session
        session['frame_count'] += 1
        session['translations'].append({
            'translation': translation_result['translation'],
            'confidence': translation_result['confidence'],
            'timestamp': timestamp
        })
        
        return jsonify({
            'success': True,
            'translation': translation_result['translation'],
            'confidence': translation_result['confidence'],
            'language': session['language'],
            'frame_count': session['frame_count']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/stop/<session_id>', methods=['POST'])
@jwt_required()
def stop_streaming(session_id):
    """Stop a streaming session"""
    try:
        user_id = get_jwt_identity()
        
        if session_id not in active_streams:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        session = active_streams[session_id]
        
        if session['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Calculate session statistics
        total_frames = session['frame_count']
        total_translations = len(session['translations'])
        duration = (datetime.now() - datetime.fromisoformat(session['started_at'])).total_seconds()
        
        # Remove session
        del active_streams[session_id]
        
        return jsonify({
            'success': True,
            'session_summary': {
                'total_frames': total_frames,
                'total_translations': total_translations,
                'duration_seconds': duration,
                'language': session['language']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@streaming_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Get active streaming sessions for the current user"""
    try:
        user_id = get_jwt_identity()
        
        user_sessions = {
            session_id: session_data 
            for session_id, session_data in active_streams.items() 
            if session_data['user_id'] == user_id
        }
        
        return jsonify({
            'success': True,
            'active_sessions': user_sessions,
            'total_sessions': len(user_sessions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_sign_language_frame(frame, language):
    """
    Process video frame for sign language recognition
    This is a placeholder - integrate with actual ML model
    """
    # Placeholder implementation
    import random
    
    sample_translations = {
        'ASL': ['Hello', 'Thank you', 'Please', 'Yes', 'No', 'Good morning', 'How are you?'],
        'BSL': ['Hello', 'Cheers', 'Please', 'Yes', 'No', 'Good morning', 'How are you?'],
        'JSL': ['こんにちは', 'ありがとう', 'お願いします', 'はい', 'いいえ', 'おはよう', '元気ですか？'],
        'LSF': ['Bonjour', 'Merci', 'S\'il vous plaît', 'Oui', 'Non', 'Bonjour', 'Comment allez-vous?'],
        'DGS': ['Hallo', 'Danke', 'Bitte', 'Ja', 'Nein', 'Guten Morgen', 'Wie geht es Ihnen?']
    }
    
    translations = sample_translations.get(language, sample_translations['ASL'])
    translation = random.choice(translations)
    confidence = round(random.uniform(0.85, 0.99), 3)
    
    return {
        'translation': translation,
        'confidence': confidence
    }
