export interface DataSource {
  name: string;
  location: { lat: number; lng: number };
  color: string;
}

export interface JurisdictionConfig {
  key: string;
  displayName: string;
  code: string;
  coordinates: [number, number]; // [longitude, latitude]
  dataSources: DataSource[];
  welcomeMessage: string;
  placeholder: string;
  regulatoryBodies: string[];
}

export const JURISDICTIONS: Record<string, JurisdictionConfig> = {
  colorado: {
    key: 'colorado',
    displayName: 'Colorado',
    code: 'CO',
    coordinates: [-105.5, 39.0],
    dataSources: [
      { name: 'Colorado Public Utilities Commission', location: { lat: 39.7392, lng: -104.9903 }, color: '#0ea5e9' },
      { name: 'Colorado Energy Office', location: { lat: 39.7392, lng: -104.9903 }, color: '#0284c7' },
      { name: 'Colorado State Legislature', location: { lat: 39.7392, lng: -104.9903 }, color: '#0369a1' },
    ],
    welcomeMessage: "Hello! I'm here to help you with Colorado energy regulations. Ask me anything about compliance, rules, or policies.",
    placeholder: 'Ask about Colorado energy regulations...',
    regulatoryBodies: ['Colorado PUC', 'Colorado Energy Office', 'Colorado Legislature'],
  },
  texas: {
    key: 'texas',
    displayName: 'Texas',
    code: 'TX',
    coordinates: [-99.9, 31.5],
    dataSources: [
      { name: 'Public Utility Commission of Texas', location: { lat: 30.2672, lng: -97.7431 }, color: '#dc2626' },
      { name: 'ERCOT', location: { lat: 30.4515, lng: -97.6665 }, color: '#ea580c' },
      { name: 'Railroad Commission of Texas', location: { lat: 30.2747, lng: -97.7404 }, color: '#d97706' },
    ],
    welcomeMessage: "Hello! I'm here to help you with Texas energy regulations. Ask me anything about PUCT rules, ERCOT protocols, or compliance.",
    placeholder: 'Ask about Texas energy regulations...',
    regulatoryBodies: ['PUCT', 'ERCOT', 'Railroad Commission of Texas'],
  },
};

export function getJurisdiction(key: string): JurisdictionConfig {
  return JURISDICTIONS[key.toLowerCase()] || JURISDICTIONS.colorado;
}

export function getSupportedJurisdictions(): JurisdictionConfig[] {
  return Object.values(JURISDICTIONS);
}
