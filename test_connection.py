from backend.supabase_client import get_supabase_client

supabase = get_supabase_client()

# Try to get some information about the database
try:
    # This might not work depending on permissions, but let's try
    response = supabase.rpc('get_tables').execute()
    print("Tables via RPC:", response.data)
except Exception as e:
    print(f"RPC get_tables failed: {e}")

# Let's try to query a common table name
common_table_names = ['users', 'user', 'players', 'player', 'profiles', 'profile']

for table_name in common_table_names:
    try:
        response = supabase.table(table_name).select('*').limit(1).execute()
        print(f"Table '{table_name}' exists! Found {len(response.data)} records")
        if response.data:
            print(f"Sample record: {response.data[0]}")
    except Exception as e:
        print(f"Table '{table_name}' does not exist or access denied: {e}")