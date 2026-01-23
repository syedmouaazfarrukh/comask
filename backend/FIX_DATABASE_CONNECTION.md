# Fix Database Connection

## Current Issue
MongoDB connection is failing with "Invalid key" error.

## Quick Fix Options

### Option 1: Get Fresh Connection String from Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Cosmos DB account: `dashgen-v1`
3. Go to **Connection String** (under Settings)
4. Click **Read-write Keys** tab
5. Copy the **PRIMARY CONNECTION STRING** again
6. Update your `.env` file with the new connection string

### Option 2: Regenerate the Key

1. In Azure Portal, go to your Cosmos DB account
2. Go to **Keys** section
3. Click **Regenerate Primary Key** (if needed)
4. Copy the new connection string
5. Update `.env`

### Option 3: Check IP Whitelist

Azure Cosmos DB might have IP restrictions:

1. Go to **Networking** in your Cosmos DB account
2. Check if **Public network access** is enabled
3. Or add your IP to the **Firewall rules**

### Option 4: Use Connection String Builder

The connection string format should be:
```
mongodb://<username>:<password>@<host>:<port>/<database>?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@<account-name>@
```

Make sure:
- Username: `dashgen-v1`
- Password: The PRIMARY KEY (not the connection string itself)
- Host: `dashgen-v1.mongo.cosmos.azure.com`
- Port: `10255`
- Database: `comask`

## For Now: Server Starts Without Database

The server is configured to start even if the database connection fails. You can:

1. **Start the server** - It will work without database
2. **Test the API** - Endpoints will work (but database features won't)
3. **Fix the connection** - Update `.env` and restart

## Test Connection

Run this to test your connection:
```bash
python scripts/test_mongodb_connection.py
```

## Update .env

Once you have the correct connection string, update your `.env` file:
```env
DATABASE_URL=mongodb://dashgen-v1:YOUR_NEW_KEY@dashgen-v1.mongo.cosmos.azure.com:10255/comask?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@dashgen-v1@
```

**Note**: Make sure to URL-encode special characters in the password if needed.

