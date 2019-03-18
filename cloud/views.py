from core import jsonify
from audit.models import cloud_log_service
from audit.models import CloudLog


def log_table(request, gtin):
    """
    Given a product's GTIN14 retrieve all status changes from teh audit table
    :param key:
    :return:
    """
    log_records = cloud_log_service.filter(username=request.user.email).order_by('-id')
    data = [{ 'id': log.id,
              'rc': log.gs1_cloud_last_rc,
              'time': log.created_at.strftime('%Y-%m-%d')
            } for log in log_records]
    return jsonify(data = data)
