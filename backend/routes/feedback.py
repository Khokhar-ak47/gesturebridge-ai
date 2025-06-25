from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

feedback_bp = Blueprint('feedback', __name__)

# In-memory storage for feedback (replace with database in production)
feedback_storage = []
translation_feedback = []

@feedback_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit user feedback for translation accuracy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        feedback_type = data.get('type')  # 'translation', 'accuracy', 'feature', 'bug'
        rating = data.get('rating')  # 1-5 scale
        comment = data.get('comment', '')
        translation_id = data.get('translation_id')
        suggested_correction = data.get('suggested_correction')
        
        if not feedback_type or rating is None:
            return jsonify({'error': 'Feedback type and rating are required'}), 400
        
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        feedback_entry = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'type': feedback_type,
            'rating': rating,
            'comment': comment,
            'translation_id': translation_id,
            'suggested_correction': suggested_correction,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        feedback_storage.append(feedback_entry)
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_entry['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/translation', methods=['POST'])
@jwt_required()
def submit_translation_feedback():
    """Submit specific feedback for a translation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        translation_id = data.get('translation_id')
        original_text = data.get('original_text')
        suggested_text = data.get('suggested_text')
        accuracy_rating = data.get('accuracy_rating')  # 1-5
        language = data.get('language')
        confidence_score = data.get('confidence_score')
        
        if not all([translation_id, accuracy_rating, language]):
            return jsonify({'error': 'Translation ID, accuracy rating, and language are required'}), 400
        
        feedback_entry = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'translation_id': translation_id,
            'original_text': original_text,
            'suggested_text': suggested_text,
            'accuracy_rating': accuracy_rating,
            'language': language,
            'confidence_score': confidence_score,
            'timestamp': datetime.now().isoformat(),
            'processed': False
        }
        
        translation_feedback.append(feedback_entry)
        
        return jsonify({
            'success': True,
            'message': 'Translation feedback submitted successfully',
            'feedback_id': feedback_entry['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/my-feedback', methods=['GET'])
@jwt_required()
def get_user_feedback():
    """Get all feedback submitted by the current user"""
    try:
        user_id = get_jwt_identity()
        
        user_feedback = [
            feedback for feedback in feedback_storage 
            if feedback['user_id'] == user_id
        ]
        
        user_translation_feedback = [
            feedback for feedback in translation_feedback 
            if feedback['user_id'] == user_id
        ]
        
        return jsonify({
            'success': True,
            'general_feedback': user_feedback,
            'translation_feedback': user_translation_feedback,
            'total_feedback': len(user_feedback) + len(user_translation_feedback)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/statistics', methods=['GET'])
def get_feedback_statistics():
    """Get overall feedback statistics"""
    try:
        total_feedback = len(feedback_storage)
        total_translation_feedback = len(translation_feedback)
        
        if total_feedback == 0:
            avg_rating = 0
        else:
            avg_rating = sum(f['rating'] for f in feedback_storage) / total_feedback
        
        if total_translation_feedback == 0:
            avg_accuracy = 0
        else:
            avg_accuracy = sum(f['accuracy_rating'] for f in translation_feedback) / total_translation_feedback
        
        # Count feedback by type
        feedback_by_type = {}
        for feedback in feedback_storage:
            feedback_type = feedback['type']
            feedback_by_type[feedback_type] = feedback_by_type.get(feedback_type, 0) + 1
        
        # Count feedback by language
        feedback_by_language = {}
        for feedback in translation_feedback:
            language = feedback['language']
            feedback_by_language[language] = feedback_by_language.get(language, 0) + 1
        
        statistics = {
            'total_feedback_entries': total_feedback,
            'total_translation_feedback': total_translation_feedback,
            'average_rating': round(avg_rating, 2),
            'average_accuracy_rating': round(avg_accuracy, 2),
            'feedback_by_type': feedback_by_type,
            'feedback_by_language': feedback_by_language,
            'recent_feedback_count': len([
                f for f in feedback_storage 
                if (datetime.now() - datetime.fromisoformat(f['timestamp'])).days <= 7
            ])
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/improve-model', methods=['POST'])
@jwt_required()
def contribute_to_model_improvement():
    """Allow users to contribute data for model improvement"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        contribution_type = data.get('type')  # 'video_sample', 'correction', 'new_gesture'
        language = data.get('language')
        gesture_description = data.get('gesture_description')
        video_data = data.get('video_data')  # Base64 encoded video
        correct_translation = data.get('correct_translation')
        
        if not all([contribution_type, language]):
            return jsonify({'error': 'Contribution type and language are required'}), 400
        
        contribution = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'type': contribution_type,
            'language': language,
            'gesture_description': gesture_description,
            'video_data': video_data,
            'correct_translation': correct_translation,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending_review',
            'reviewed_by': None,
            'approved': False
        }
        
        # Store contribution (in production, this would go to a database)
        # For now, we'll just acknowledge the contribution
        
        return jsonify({
            'success': True,
            'message': 'Thank you for contributing to model improvement!',
            'contribution_id': contribution['id'],
            'points_earned': 10  # Gamification element
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/report-issue', methods=['POST'])
@jwt_required()
def report_issue():
    """Report technical issues or bugs"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        issue_type = data.get('type')  # 'bug', 'performance', 'feature_request', 'accessibility'
        title = data.get('title')
        description = data.get('description')
        severity = data.get('severity', 'medium')  # low, medium, high, critical
        browser_info = data.get('browser_info')
        device_info = data.get('device_info')
        
        if not all([issue_type, title, description]):
            return jsonify({'error': 'Issue type, title, and description are required'}), 400
        
        issue = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'type': issue_type,
            'title': title,
            'description': description,
            'severity': severity,
            'browser_info': browser_info,
            'device_info': device_info,
            'timestamp': datetime.now().isoformat(),
            'status': 'open',
            'assigned_to': None
        }
        
        # Store issue report
        feedback_storage.append(issue)
        
        return jsonify({
            'success': True,
            'message': 'Issue reported successfully',
            'issue_id': issue['id'],
            'estimated_response_time': '24-48 hours'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/feature-request', methods=['POST'])
@jwt_required()
def submit_feature_request():
    """Submit a feature request"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        description = data.get('description')
        priority = data.get('priority', 'medium')  # low, medium, high
        use_case = data.get('use_case')
        expected_benefit = data.get('expected_benefit')
        
        if not all([title, description]):
            return jsonify({'error': 'Title and description are required'}), 400
        
        feature_request = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': title,
            'description': description,
            'priority': priority,
            'use_case': use_case,
            'expected_benefit': expected_benefit,
            'timestamp': datetime.now().isoformat(),
            'status': 'under_review',
            'votes': 1,  # User automatically votes for their own request
            'voters': [user_id]
        }
        
        feedback_storage.append(feature_request)
        
        return jsonify({
            'success': True,
            'message': 'Feature request submitted successfully',
            'request_id': feature_request['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/vote/<request_id>', methods=['POST'])
@jwt_required()
def vote_for_feature(request_id):
    """Vote for a feature request"""
    try:
        user_id = get_jwt_identity()
        
        # Find the feature request
        feature_request = None
        for feedback in feedback_storage:
            if feedback.get('id') == request_id and 'votes' in feedback:
                feature_request = feedback
                break
        
        if not feature_request:
            return jsonify({'error': 'Feature request not found'}), 404
        
        if user_id in feature_request.get('voters', []):
            return jsonify({'error': 'You have already voted for this feature'}), 400
        
        # Add vote
        feature_request['votes'] += 1
        feature_request['voters'].append(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Vote recorded successfully',
            'total_votes': feature_request['votes']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
