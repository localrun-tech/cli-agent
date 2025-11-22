import {Command, Flags} from '@oclif/core'
import express from 'express'
import {homedir} from 'os'
import {join} from 'path'
import {writeFileSync} from 'fs'
import chalk from 'chalk'
import {getHostInfo} from '../lib/system/host'
import {getOpenPorts} from '../lib/system/ports'
import {getProcesses} from '../lib/system/processes'
import {getDockerContainers} from '../lib/system/docker'

export default class Serve extends Command {
  static description = 'Start agent HTTP server (used by LaunchAgent)'

  static examples = [
    '<%= config.bin %> <%= command.id %>',
    '<%= config.bin %> <%= command.id %> --port 47777',
  ]

  static flags = {
    port: Flags.integer({char: 'p', description: 'Server port', default: 47777}),
    host: Flags.string({char: 'h', description: 'Server host', default: '127.0.0.1'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(Serve)

    const app = express()
    app.use(express.json())

    app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*')
      res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
      res.header('Access-Control-Allow-Headers', 'Content-Type')
      if (req.method === 'OPTIONS') {
        res.sendStatus(200)
      } else {
        next()
      }
    })

    // Health check
    app.get('/api/ping', (req, res) => {
      res.json({
        status: 'ok',
        service: 'localrun-agent',
        version: this.config.version,
        timestamp: new Date().toISOString(),
      })
    })

    app.get('/api/host/info', async (req, res) => {
      try {
        const info = await getHostInfo()
        res.json(info)
      } catch (error) {
        res.status(500).json({error: (error as Error).message})
      }
    })

    app.get('/api/host/ports', async (req, res) => {
      try {
        const ports = await getOpenPorts()
        res.json({ports})
      } catch (error) {
        res.status(500).json({error: (error as Error).message})
      }
    })

    app.get('/api/host/processes', async (req, res) => {
      try {
        const processes = await getProcesses()
        res.json({processes})
      } catch (error) {
        res.status(500).json({error: (error as Error).message})
      }
    })

    app.get('/api/docker/containers', async (req, res) => {
      try {
        const containers = await getDockerContainers()
        res.json({containers})
      } catch (error) {
        res.status(500).json({error: (error as Error).message})
      }
    })

    app.listen(flags.port, flags.host, () => {
      this.log(chalk.green('✓') + ` LocalRun Agent listening on ${chalk.blue(`http://${flags.host}:${flags.port}`)}`)

      // Save config
      const configPath = join(homedir(), '.localrun', 'agent.json')
      writeFileSync(configPath, JSON.stringify({
        port: flags.port,
        version: this.config.version,
        pid: process.pid,
        started_at: new Date().toISOString(),
      }, null, 2))
    })
  }
}
