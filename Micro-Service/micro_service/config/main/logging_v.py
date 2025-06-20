from utils.helper import create_dir
import logging
class SysLogging:
    def __init__(self,**kwargs):
        self.logger = kwargs
    def get_logger(self):
        return self.logger
 

# Log directories


def creating_loging_config(LOG):
    
    SYS_LOG = create_dir(LOG / 'system')
    SETTINGS_LOG = create_dir(LOG / 'settings')
    UTILS_LOG = create_dir(LOG / 'utils')
    VIEW_LOG = create_dir(LOG / 'views')
    TEST_LOG = create_dir(LOG / 'tests')
    MODEL_LOG = create_dir(LOG / 'models')   
        
    return  {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s [%(levelname)s] %(name)s | %(message)s',
            },
            'simple': {
                'format': '[%(levelname)s] %(message)s',
            },
        },
        'handlers': {
            'system_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(SYS_LOG / 'system.log'),
                'maxBytes': 1024 * 1024 * 5,
                'backupCount': 5,
                'formatter': 'verbose',
            },
            'settings_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': SETTINGS_LOG / 'settings.log',
                'maxBytes': 1024 * 1024 * 2,
                'backupCount': 3,
                'formatter': 'verbose',
            },
            'utils_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': UTILS_LOG / 'utils.log',
                'maxBytes': 1024 * 1024 * 2,
                'backupCount': 3,
                'formatter': 'verbose',
            },
            'views_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': VIEW_LOG / 'views.log',
                'maxBytes': 1024 * 1024 * 2,
                'backupCount': 3,
                'formatter': 'verbose',
            },
            'models_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': MODEL_LOG / 'model.log',
                'maxBytes': 1024 * 1024 * 2,
                'backupCount': 3,
                'formatter': 'verbose',
            },
            'tests_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': TEST_LOG / 'tests.log',
                'maxBytes': 1024 * 1024 * 2,
                'backupCount': 3,
                'formatter': 'verbose',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            }
        },
    
         'loggers': {
            'system': {
                'handlers': ['system_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'settings': {
                'handlers': ['settings_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'utils': {
                'handlers': ['utils_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'views': {
                'handlers': ['views_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'models': {
                'handlers': ['models_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'tests': {
                'handlers': ['tests_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }


if __name__ == '__main__':
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))
    print(SysLogging(name = "My name", data = "My Data"))











