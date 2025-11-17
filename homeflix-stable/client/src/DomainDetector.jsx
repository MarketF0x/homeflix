// Détection intelligente du nom de domaine selon la source de connexion
// homeone.local (réseau local) / homeone.wifi (WiFi) / homeone.web (Tailscale/distant)

import { useState, useEffect } from 'react';

export function useDomainName() {
  const [domainName, setDomainName] = useState('HomeOne');
  const [connectionType, setConnectionType] = useState('local');

  useEffect(() => {
    const hostname = window.location.hostname;
    
    // Détection basée sur le hostname
    if (hostname.includes('homeone.wifi')) {
      setDomainName('HomeOne WiFi');
      setConnectionType('wifi');
    } else if (hostname.includes('homeone.web')) {
      setDomainName('HomeOne Web');
      setConnectionType('web');
    } else if (hostname.includes('homeone.lan')) {
      setDomainName('HomeOne LAN');
      setConnectionType('lan');
    } else if (hostname.includes('homeone.local')) {
      setDomainName('HomeOne Local');
      setConnectionType('local');
    } else if (hostname.includes('homeone')) {
      setDomainName('HomeOne');
      setConnectionType('tailscale');
    }
    // Détection basée sur l'IP
    else if (hostname.startsWith('100.')) {
      setDomainName('HomeOne Web');
      setConnectionType('web');
    } else if (hostname.startsWith('192.168.') || hostname.startsWith('10.')) {
      setDomainName('HomeOne WiFi');
      setConnectionType('wifi');
    } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
      setDomainName('HomeOne Local');
      setConnectionType('local');
    } else {
      setDomainName('HomeOne');
      setConnectionType('unknown');
    }

    console.log('🌐 Domaine détecté:', domainName, '| Type:', connectionType, '| Hostname:', hostname);
  }, []);

  return { domainName, connectionType };
}

export function DomainBadge() {
  const { domainName, connectionType } = useDomainName();

  const getIcon = () => {
    switch (connectionType) {
      case 'wifi': return '📡';
      case 'web': return '🌍';
      case 'lan': return '🔌';
      case 'tailscale': return '🔗';
      case 'local': return '🏠';
      default: return '🌐';
    }
  };

  const getColor = () => {
    switch (connectionType) {
      case 'wifi': return '#fbbf24'; // yellow-400
      case 'web': return '#3b82f6'; // blue-500
      case 'lan': return '#8b5cf6'; // purple-500
      case 'tailscale': return '#10b981'; // green-500
      case 'local': return '#6b7280'; // gray-500
      default: return '#6b7280';
    }
  };

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.25rem 0.75rem',
        borderRadius: '9999px',
        backgroundColor: `${getColor()}20`,
        color: getColor(),
        fontSize: '0.875rem',
        fontWeight: '500',
        border: `1px solid ${getColor()}40`,
      }}
      title={`Connecté via ${connectionType}`}
    >
      <span>{getIcon()}</span>
      <span>{domainName}</span>
    </div>
  );
}

export default function NetworkInfo() {
  const { domainName, connectionType } = useDomainName();
  const [showDetails, setShowDetails] = useState(false);

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const port = window.location.port;

  return (
    <div style={{ 
      position: 'fixed', 
      top: '1rem', 
      right: '1rem', 
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-end',
      gap: '0.5rem'
    }}>
      <button
        onClick={() => setShowDetails(!showDetails)}
        style={{
          background: 'rgba(0, 0, 0, 0.8)',
          border: 'none',
          padding: '0.5rem',
          borderRadius: '0.5rem',
          cursor: 'pointer',
          backdropFilter: 'blur(10px)',
        }}
      >
        <DomainBadge />
      </button>

      {showDetails && (
        <div
          style={{
            background: 'rgba(0, 0, 0, 0.95)',
            padding: '1rem',
            borderRadius: '0.5rem',
            color: 'white',
            fontSize: '0.875rem',
            minWidth: '250px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>
            📊 Informations de connexion
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.75rem' }}>
            <div>
              <span style={{ opacity: 0.7 }}>Domaine :</span>{' '}
              <span style={{ fontWeight: '500' }}>{domainName}</span>
            </div>
            <div>
              <span style={{ opacity: 0.7 }}>Type :</span>{' '}
              <span style={{ fontWeight: '500' }}>
                {connectionType === 'wifi' && 'WiFi Local'}
                {connectionType === 'web' && 'Accès distant (Tailscale)'}
                {connectionType === 'lan' && 'Ethernet'}
                {connectionType === 'local' && 'Local (localhost)'}
                {connectionType === 'tailscale' && 'Tailscale MagicDNS'}
                {connectionType === 'unknown' && 'Inconnu'}
              </span>
            </div>
            <div>
              <span style={{ opacity: 0.7 }}>URL :</span>{' '}
              <span style={{ fontFamily: 'monospace', fontSize: '0.7rem' }}>
                {protocol}//{hostname}{port ? `:${port}` : ''}
              </span>
            </div>
            <div>
              <span style={{ opacity: 0.7 }}>Protocole :</span>{' '}
              <span style={{ fontWeight: '500' }}>
                {protocol === 'https:' ? '🔒 HTTPS' : '🔓 HTTP'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

