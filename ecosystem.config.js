
module.exports = {
    apps: [{
        name: 'celery',
        script: 'celery -A NLP -c 2 worker -l error',
        instances: 1,
        autorestart: true,
        watch: false,
        max_memory_restart: '1G',
        error_file: 'log/celeryErr.log',
        out_file: 'log/celeryOut.log',
        log_data_format: 'YYYY-MM-DD HH:mm:ss',
        merge_logs: true,
        env: {
            NODE_ENV: 'development'
        },
        env_production: {
            NODE_ENV: 'production'
        }
    },
        {
            name: 'nlp',
            script: 'manage.py',
            args: 'runserver 0.0.0.0:80 --insecure',
            instances: 1,
            interpreter: 'python3',
            autorestart: true,
            watch: false,
            error: '/dev/null',
            output: '/dev/null',
            max_memory_restart: '1G',
            env: {
                NODE_ENV: 'development'
            },
            env_production: {
                NODE_ENV: 'production'
            }
        }]
};

