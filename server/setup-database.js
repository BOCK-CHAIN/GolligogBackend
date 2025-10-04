const { Client } = require('pg');
require('dotenv').config();

const testDirectConnection = async () => {
    // Parse the DATABASE_URL
    const databaseUrl = process.env.DATABASE_URL;
    console.log('Testing direct PostgreSQL connection to Neon...\n');
    
    const client = new Client({
        connectionString: databaseUrl,
        ssl: {
            rejectUnauthorized: false
        }
    });

    try {
        console.log('🔌 Connecting to Neon PostgreSQL...');
        await client.connect();
        console.log('✅ Successfully connected to Neon!');
        
        // Test basic query
        const version = await client.query('SELECT version()');
        console.log('📊 PostgreSQL version:', version.rows[0].version.split(' ')[0]);
        
        // Create users table manually
        console.log('\n📋 Creating users table...');
        await client.query(`
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        `);
        console.log('✅ Users table created successfully!');
        
        // Check table exists
        const tableCheck = await client.query(`
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'users'
        `);
        
        if (tableCheck.rows.length > 0) {
            console.log('✅ Users table verified in database');
            
            // Count existing users
            const userCount = await client.query('SELECT COUNT(*) FROM users');
            console.log(`👥 Current users in database: ${userCount.rows[0].count}`);
        }
        
        console.log('\n🎉 Database setup completed successfully!');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await client.end();
        console.log('🔌 Disconnected from database');
    }
};

testDirectConnection();
