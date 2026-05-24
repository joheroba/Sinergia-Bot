import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def delete_latest_post():
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    short_token = os.getenv("FACEBOOK_SHORT_TOKEN")
    
    print(">> Iniciando proceso de eliminación en Immunotec La Molina...")
    
    async with aiohttp.ClientSession() as session:
        # 1. Obtener Long Token
        url = f"https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_token}"
        async with session.get(url) as response:
            res_data = await response.json()
            long_token = res_data.get("access_token")
            if not long_token:
                print("Error obteniendo token:", res_data)
                return

        # 2. Obtener Token de la página Immunotec La Molina
        page_id_immunotec = "109973247580990"
        pt_url = f"https://graph.facebook.com/v20.0/{page_id_immunotec}?fields=access_token&access_token={long_token}"
        async with session.get(pt_url) as pt_resp:
            pt_data = await pt_resp.json()
            page_token = pt_data.get("access_token")
            if not page_token:
                print("Error obteniendo token de la página:", pt_data)
                return
        
        # 3. Obtener el último post
        posts_url = f"https://graph.facebook.com/v20.0/{page_id_immunotec}/posts?limit=5&access_token={page_token}"
        async with session.get(posts_url) as posts_resp:
            posts_data = await posts_resp.json()
            data = posts_data.get("data", [])
            if not data:
                print("No se encontraron publicaciones en la página.")
                return
            
            latest_post = data[0]
            post_id = latest_post.get("id")
            mensaje = latest_post.get("message", "Sin texto")
            print(f">> Última publicación encontrada:")
            print(f"   ID: {post_id}")
            print(f"   Mensaje: {mensaje[:50]}...")
            
            # 4. Eliminar el post
            delete_url = f"https://graph.facebook.com/v20.0/{post_id}?access_token={page_token}"
            async with session.delete(delete_url) as del_resp:
                del_data = await del_resp.json()
                if del_data.get("success"):
                    print(">> ¡Publicación eliminada exitosamente!")
                else:
                    print(">> Error al eliminar:", del_data)

if __name__ == "__main__":
    asyncio.run(delete_latest_post())
