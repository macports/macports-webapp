module.exports = {
  apps: [
    {
      name: 'macports-ui',
      script: 'npm',
      args: 'start',
      instances: 'max', // or specify a number like 4
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      min_uptime: '10s',
      max_restarts: 10,
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ]
};

