import { useEffect, useState, useRef, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000'

interface UseSocketReturn {
  socket: Socket | null
  connected: boolean
  connect: () => void
  disconnect: () => void
}

export function useSocket(): UseSocketReturn {
  const [connected, setConnected] = useState(false)
  const socketRef = useRef<Socket | null>(null)

  const connect = useCallback(() => {
    if (socketRef.current?.connected) return

    const socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
    })

    socket.on('connect', () => {
      console.log('Socket connected:', socket.id)
      setConnected(true)
    })

    socket.on('disconnect', () => {
      console.log('Socket disconnected')
      setConnected(false)
    })

    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error)
      setConnected(false)
    })

    socketRef.current = socket
  }, [])

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect()
      socketRef.current = null
      setConnected(false)
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    socket: socketRef.current,
    connected,
    connect,
    disconnect,
  }
}
