import * as dotenv from 'dotenv';
import mineflayer from 'mineflayer';
import { createServer } from 'http';
import pino from 'pino';

dotenv.config();

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
    },
  },
});

const config = {
  host: process.env.MINECRAFT_SERVER_HOST || 'localhost',
  port: parseInt(process.env.MINECRAFT_SERVER_PORT || '25565'),
  username: process.env.MINECRAFT_BOT_USERNAME || 'Bot',
  version: process.env.MINECRAFT_VERSION || '1.21.10',
};

logger.info({ config }, 'Starting Minecraft bot with configuration');

let bot: mineflayer.Bot | null = null;
let isConnected = false;
let reconnectTimeout: NodeJS.Timeout | null = null;

function scheduleReconnect(reason: string, delay: number = 5000) {
  if (reconnectTimeout) {
    logger.debug('Reconnection already scheduled, skipping duplicate');
    return;
  }
  
  logger.info({ reason, delay }, 'Scheduling reconnection');
  reconnectTimeout = setTimeout(() => {
    reconnectTimeout = null;
    createBot();
  }, delay);
}

function createBot() {
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }

  if (bot) {
    logger.debug('Cleaning up previous bot instance');
    bot.removeAllListeners();
    try {
      bot.quit();
    } catch (err) {
      logger.debug({ err }, 'Error during bot cleanup (safe to ignore)');
    }
    bot = null;
  }

  try {
    logger.info('Creating new bot instance');
    bot = mineflayer.createBot({
      host: config.host,
      port: config.port,
      username: config.username,
      version: config.version as any,
      auth: 'offline',
    });

    bot.on('login', () => {
      isConnected = true;
      logger.info(`Bot logged in as ${bot?.username}`);
      logger.info(`Position: ${bot?.entity.position}`);
    });

    bot.on('spawn', () => {
      logger.info('Bot spawned in the world');
      if (bot?.game) {
        logger.info(`Game mode: ${bot.game.gameMode}`);
        logger.info(`Difficulty: ${bot.game.difficulty}`);
      }
    });

    bot.on('chat', (username, message) => {
      if (username === bot?.username) return;
      logger.info({ username, message }, 'Chat message received');
    });

    bot.on('error', (err) => {
      logger.error({ err }, 'Bot error occurred');
      isConnected = false;
    });

    bot.on('kicked', (reason) => {
      logger.warn({ reason }, 'Bot was kicked from server');
      isConnected = false;
    });

    bot.on('end', (reason) => {
      logger.info({ reason }, 'Bot disconnected');
      isConnected = false;
      scheduleReconnect(reason || 'unknown');
    });

    bot.on('death', () => {
      logger.warn('Bot died, respawning...');
      if (bot) {
        bot.chat('Respawned after death');
      }
    });

    bot.on('messagestr', (message) => {
      logger.debug({ message }, 'Server message');
    });

  } catch (error) {
    logger.error({ error }, 'Failed to create bot');
    isConnected = false;
    scheduleReconnect('creation_error');
  }
}

const server = createServer((req, res) => {
  if (req.url === '/health') {
    const status = {
      status: isConnected ? 'connected' : 'disconnected',
      bot: bot?.username || 'not initialized',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(status, null, 2));
  } else {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Minecraft Bot Server Running\n');
  }
});

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  logger.info(`Health check server listening on port ${PORT}`);
  logger.info(`Health endpoint: http://localhost:${PORT}/health`);
  createBot();
});

process.on('SIGINT', () => {
  logger.info('Shutting down gracefully...');
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
  }
  if (bot) {
    bot.quit();
  }
  server.close();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Received SIGTERM, shutting down...');
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
  }
  if (bot) {
    bot.quit();
  }
  server.close();
  process.exit(0);
});
