"""
Routes for ics ot endpoints.
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
import uuid
import random
import json
import time

from . import ics_ot_router
from app.models import *
from app.routing import get_json_or_default

@ics_ot_router.route('/api/ics/scada/systems')
async def ics_scada_systems(request: Request):
    """SCADA systems inventory - reconnaissance target"""
    return JSONResponse({
        'scada_systems': [
            {
                'system_id': 'SCADA-001',
                'name': 'Water Treatment Plant Alpha',
                'vendor': 'Schneider Electric',
                'model': 'EcoStruxure SCADA Expert',
                'location': 'Facility-North',
                'protocol': 'DNP3',
                'status': 'operational',
                'hmi_access': 'http://10.20.30.100:8080',
                'last_maintenance': '2024-11-15'
            },
            {
                'system_id': 'SCADA-002',
                'name': 'Power Distribution Control',
                'vendor': 'Siemens',
                'model': 'WinCC SCADA',
                'location': 'Substation-East',
                'protocol': 'IEC 61850',
                'status': 'operational',
                'hmi_access': 'http://10.20.30.101:8080',
                'last_maintenance': '2024-12-01'
            },
            {
                'system_id': 'SCADA-003',
                'name': 'Manufacturing Line Control',
                'vendor': 'Rockwell Automation',
                'model': 'FactoryTalk View SE',
                'location': 'Production-Floor-2',
                'protocol': 'EtherNet/IP',
                'status': 'maintenance',
                'hmi_access': 'http://10.20.30.102:8080',
                'last_maintenance': '2024-12-08'
            }
        ],
        'total_systems': 3,
        'network_segments': ['OT-DMZ', 'Control-LAN', 'Field-Network'],
        'security_level': 'basic',
        'authentication_required': False
    })


@ics_ot_router.route('/api/plc/commands/send', methods=['POST'])
async def plc_commands_send(request: Request):
    """Send commands to PLC - critical control manipulation"""
    data = await get_json_or_default(request)
    plc_id = data.get('plc_id', '')
    command = data.get('command', '')
    register = data.get('register', '')
    value = data.get('value', 0)
    return JSONResponse({
        'plc_id': plc_id,
        'command': command,
        'register': register,
        'value': value,
        'command_accepted': True,
        'safety_interlocks_bypassed': True,
        'execution_mode': 'unsafeguarded'
    }, status_code=201)


@ics_ot_router.route('/api/ot/devices/inventory')
async def ot_devices_inventory(request: Request):
    """OT devices inventory - attack surface mapping"""
    return JSONResponse({
        'devices': [
            {
                'device_id': 'PLC-101',
                'type': 'Programmable Logic Controller',
                'vendor': 'Allen Bradley',
                'model': 'ControlLogix 5580',
                'ip_address': '10.50.1.101',
                'firmware': '32.011',
                'protocol': 'EtherNet/IP',
                'function': 'Reactor Temperature Control',
                'criticality': 'high',
                'last_scan': '2024-12-08T10:30:00Z'
            },
            {
                'device_id': 'RTU-201',
                'type': 'Remote Terminal Unit',
                'vendor': 'ABB',
                'model': 'RTU560',
                'ip_address': '10.50.1.201',
                'firmware': '5.2.1',
                'protocol': 'Modbus TCP',
                'function': 'Pipeline Pressure Monitoring',
                'criticality': 'critical',
                'last_scan': '2024-12-08T10:28:00Z'
            },
            {
                'device_id': 'HMI-301',
                'type': 'Human Machine Interface',
                'vendor': 'Wonderware',
                'model': 'InTouch 2020',
                'ip_address': '10.50.1.301',
                'firmware': '2020.R2',
                'protocol': 'OPC UA',
                'function': 'Operator Workstation',
                'criticality': 'medium',
                'last_scan': '2024-12-08T10:25:00Z'
            },
            {
                'device_id': 'IED-401',
                'type': 'Intelligent Electronic Device',
                'vendor': 'GE Grid Solutions',
                'model': 'D60 Line Distance Relay',
                'ip_address': '10.50.1.401',
                'firmware': '7.30',
                'protocol': 'IEC 61850',
                'function': 'Power Line Protection',
                'criticality': 'critical',
                'last_scan': '2024-12-08T10:32:00Z'
            }
        ],
        'total_devices': 4,
        'vulnerable_devices': 2,
        'unpatched_devices': 3,
        'default_credentials': ['PLC-101'],
        'exposed_services': ['telnet', 'ftp', 'http'],
        'network_segmentation': 'poor'
    })


@ics_ot_router.route('/api/ics/setpoints/modify', methods=['PUT'])
async def ics_setpoints_modify(request: Request):
    """Modify industrial process setpoints - sabotage vector"""
    data = await get_json_or_default(request)
    controller_id = data.get('controller_id', '')
    parameter = data.get('parameter', '')
    new_value = data.get('new_value', 0)
    override_safety = data.get('override_safety', False)
    return JSONResponse({
        'controller_id': controller_id,
        'parameter': parameter,
        'new_value': new_value,
        'override_safety': override_safety,
        'setpoint_updated': True,
        'process_integrity': 'compromised'
    })


@ics_ot_router.route('/api/ot/protocols/modbus', methods=['POST'])
async def ot_protocols_modbus(request: Request):
    """Modbus protocol operations - industrial protocol exploitation"""
    data = await get_json_or_default(request)
    function_code = data.get('function_code', 3)
    slave_id = data.get('slave_id', 1)
    register_address = data.get('register_address', 40001)
    quantity = data.get('quantity', 10)
    return JSONResponse({
        'function_code': function_code,
        'slave_id': slave_id,
        'register_address': register_address,
        'quantity': quantity,
        'operation_completed': True,
        'protocol_security': 'none'
    }, status_code=201)


@ics_ot_router.route('/api/ics/hmi/interfaces')
async def ics_hmi_interfaces(request: Request):
    """HMI interface discovery - operator interface targeting"""
    return JSONResponse({
        'hmi_interfaces': [
            {
                'hmi_id': 'HMI-MAIN-01',
                'name': 'Main Control Room',
                'vendor': 'Siemens',
                'product': 'WinCC Unified',
                'version': '17.0',
                'url': 'http://10.40.5.100',
                'port': 80,
                'authentication': 'basic',
                'default_credentials': 'admin:admin',
                'screens': ['overview', 'alarms', 'trends', 'diagnostics'],
                'active_sessions': 3,
                'privilege_level': 'administrator',
                'remote_access_enabled': True
            },
            {
                'hmi_id': 'HMI-FIELD-02',
                'name': 'Field Operator Station',
                'vendor': 'Wonderware',
                'product': 'System Platform',
                'version': '2023',
                'url': 'http://10.40.5.101',
                'port': 80,
                'authentication': 'none',
                'default_credentials': None,
                'screens': ['local_control', 'setpoints', 'manual_override'],
                'active_sessions': 1,
                'privilege_level': 'operator',
                'remote_access_enabled': True
            }
        ],
        'total_interfaces': 2,
        'unauthenticated_access': 1,
        'weak_credentials': 1,
        'command_injection_vulnerable': True,
        'session_hijacking_possible': True
    })


@ics_ot_router.route('/api/ot/safety/bypass', methods=['POST'])
async def ot_safety_bypass(request: Request):
    """Bypass safety instrumented systems - critical safety compromise"""
    data = await get_json_or_default(request)
    sis_id = data.get('sis_id', '')
    bypass_reason = data.get('bypass_reason', '')
    duration_minutes = data.get('duration_minutes', 60)
    return JSONResponse({
        'sis_id': sis_id,
        'bypass_reason': bypass_reason,
        'duration_minutes': duration_minutes,
        'bypass_enabled': True,
        'operator_confirmation_required': False
    }, status_code=201)


@ics_ot_router.route('/api/ics/schedules/manipulate', methods=['PUT'])
async def ics_schedules_manipulate(request: Request):
    """Manipulate production schedules - operational disruption"""
    data = await get_json_or_default(request)
    schedule_id = data.get('schedule_id', '')
    modifications = data.get('modifications', {})
    return JSONResponse({
        'schedule_id': schedule_id,
        'modifications': modifications,
        'changes_applied': len(modifications),
        'approval_bypassed': True
    })


@ics_ot_router.route('/api/ics/controllers/status')
async def ics_controllers_status(request: Request):
    """Industrial controller status - operational intelligence"""
    return JSONResponse({
        'controllers': [
            {
                'controller_id': 'DCS-001',
                'type': 'Distributed Control System',
                'vendor': 'Emerson DeltaV',
                'status': 'running',
                'cpu_usage': random.uniform(25, 75),
                'memory_usage': random.uniform(40, 80),
                'io_modules': 24,
                'active_loops': 156,
                'alarms_active': random.randint(0, 5),
                'mode': 'automatic',
                'last_restart': '2024-11-20T08:00:00Z',
                'uptime_hours': 432
            },
            {
                'controller_id': 'PAC-002',
                'type': 'Programmable Automation Controller',
                'vendor': 'Rockwell CompactLogix',
                'status': 'running',
                'cpu_usage': random.uniform(15, 60),
                'memory_usage': random.uniform(30, 70),
                'io_modules': 12,
                'active_loops': 48,
                'alarms_active': random.randint(0, 3),
                'mode': 'automatic',
                'last_restart': '2024-12-01T06:00:00Z',
                'uptime_hours': 168
            }
        ],
        'total_controllers': 2,
        'controllers_in_fault': 0,
        'controllers_in_manual': 0,
        'system_health': 'good',
        'redundancy_status': 'active-standby',
        'network_latency_ms': random.randint(5, 25)
    })


@ics_ot_router.route('/api/ot/network/segment', methods=['POST'])
async def ot_network_segment(request: Request):
    """OT network segmentation operations - lateral movement"""
    data = await get_json_or_default(request)
    source_segment = data.get('source_segment', '')
    target_segment = data.get('target_segment', '')
    bypass_firewall = data.get('bypass_firewall', False)
    return JSONResponse({
        'source_segment': source_segment,
        'target_segment': target_segment,
        'bypass_firewall': bypass_firewall,
        'segmentation_modified': True,
        'lateral_movement_enabled': True
    }, status_code=201)

