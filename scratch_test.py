import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

def mask_token(token):
    if not token:
        return "None"
    if len(token) <= 20:
        return token
    return f"{token[:10]}...{token[-10:]} ({len(token)} chars)"

async def main():
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    short_token = os.getenv("FACEBOOK_SHORT_TOKEN")
    
    print("=== DIAGNÓSTICO COMPLETO v3 ===\n")
    
    async with aiohttp.ClientSession() as session:
        # 1. Obtener long token
        print(">> 1. Obteniendo Long Token...")
        url = f"https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_token}"
        async with session.get(url) as response:
            res_data = await response.json()
            if response.status != 200:
                print(f"ERROR: {res_data}")
                return
            long_token = res_data.get("access_token")
            print(f"ÉXITO! Long Token: {mask_token(long_token)}")
        
        # 2. ¿Quién soy yo? (verificar identidad del usuario)
        print("\n>> 2. Verificando identidad del usuario (me?fields=id,name)...")
        me_url = f"https://graph.facebook.com/v20.0/me?fields=id,name&access_token={long_token}"
        async with session.get(me_url) as me_resp:
            me_data = await me_resp.json()
            print(f"Resultado: {me_data}")
            my_id = me_data.get("id", "desconocido")
        
        # 3. Lista de páginas
        print("\n>> 3. Páginas en /me/accounts (limit=100)...")
        pages_url = f"https://graph.facebook.com/v20.0/me/accounts?limit=100&fields=id,name,access_token,tasks&access_token={long_token}"
        async with session.get(pages_url) as pages_resp:
            pages_data = await pages_resp.json()
            pages_list = pages_data.get("data", [])
            print(f"Total: {len(pages_list)} páginas")
            for idx, p in enumerate(pages_list):
                print(f"  [{idx+1}] {p.get('name')} (ID: {p.get('id')}) Tasks: {p.get('tasks', 'N/A')}")
        
        # 4. Probar múltiples IDs posibles para Gano Excel
        test_ids = ["100080372792708", "474043802663478"]
        for test_id in test_ids:
            print(f"\n>> 4. Consultando ID {test_id} directamente...")
            
            # 4a. Con long token
            info_url = f"https://graph.facebook.com/v20.0/{test_id}?fields=id,name,about,link,category&access_token={long_token}"
            async with session.get(info_url) as info_resp:
                info_data = await info_resp.json()
                if info_resp.status == 200:
                    print(f"  ÉXITO con long token: {info_data}")
                else:
                    error_msg = info_data.get('error', {}).get('message', 'Unknown')
                    print(f"  Error con long token: {error_msg}")
            
            # 4b. Intentar obtener access_token de la página
            pt_url = f"https://graph.facebook.com/v20.0/{test_id}?fields=access_token,name&access_token={long_token}"
            async with session.get(pt_url) as pt_resp:
                pt_data = await pt_resp.json()
                if pt_resp.status == 200 and "access_token" in pt_data:
                    print(f"  Page Token obtenido: {mask_token(pt_data.get('access_token'))}")
                else:
                    print(f"  No se pudo obtener Page Token")

        # 5. Probar con el short token original (a veces funciona diferente)
        print(f"\n>> 5. Probando IDs con el short token original...")
        for test_id in test_ids:
            info_url = f"https://graph.facebook.com/v20.0/{test_id}?fields=id,name&access_token={short_token}"
            async with session.get(info_url) as info_resp:
                info_data = await info_resp.json()
                if info_resp.status == 200:
                    print(f"  {test_id} con short token: ÉXITO - {info_data}")
                else:
                    error_msg = info_data.get('error', {}).get('message', 'Unknown')
                    print(f"  {test_id} con short token: Error - {error_msg}")
        
        # 6. Verificar permisos del token
        print(f"\n>> 6. Verificando permisos incluidos en el token...")
        debug_url = f"https://graph.facebook.com/v20.0/debug_token?input_token={long_token}&access_token={app_id}|{app_secret}"
        async with session.get(debug_url) as debug_resp:
            debug_data = await debug_resp.json()
            token_data = debug_data.get("data", {})
            scopes = token_data.get("scopes", [])
            print(f"  Permisos (scopes): {scopes}")
            print(f"  User ID: {token_data.get('user_id')}")
            print(f"  App ID: {token_data.get('app_id')}")
            print(f"  Válido: {token_data.get('is_valid')}")
            expires = token_data.get("expires_at", 0)
            if expires:
                from datetime import datetime
                print(f"  Expira: {datetime.fromtimestamp(expires)}")

if __name__ == "__main__":
    asyncio.run(main())
