import React from 'react'
import { Providers }  from './app/providers'
import { AppShell }   from './app/AppShell'

export default function App() {
  return (
    <Providers>
      <AppShell />
    </Providers>
  )
}
