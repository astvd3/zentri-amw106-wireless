/*
 * ZentriOS SDK LICENSE AGREEMENT | Zentri.com, 2015.
 *
 * Use of source code and/or libraries contained in the ZentriOS SDK is
 * subject to the Zentri Operating System SDK license agreement and
 * applicable open source license agreements.
 *
 */
/* Documentation for this app is available online.
 * See https://docs.zentri.com/wifi/sdk/latest/examples/basic/web-setup
 */

#include "zos.h"

static zos_bool_t running;


/*************************************************************************************************/
void zn_app_init(void)
{
    zos_result_t result;
    char buffer[96];
    char buffer2[128];
    uint32_t setup_done=0;
    ZOS_LOG("Starting Web Setup App ...");
    if(zn_load_app_settings("settings.ini") != ZOS_SUCCESS){
        ZOS_LOG("Failed to load settings");
        return;
    }
    zn_setup_register_client_event_handler(setup_client_event_handler);
    zn_setup_register_finished_event_handler(setup_finished_event_handler);
    zn_nvm_read(&setup_done,20,4);
        ZOS_LOG("%d",setup_done);
    if(setup_done!=1){
		if(ZOS_FAILED(result, zn_setup_start()))
		{
			ZOS_LOG("Failed to start web setup, error code: %d", result);
			return;
		}

		ZOS_LOG("Web setup running ...");
		ZOS_LOG("Wi-Fi network: %s", ZOS_GET_SETTING_STR("setup.web.ssid", buffer));
		ZOS_LOG("     password: %s", ZOS_GET_SETTING_STR("setup.web.passkey", buffer));
		ZOS_LOG("  HTTP URL(s): %s", ZOS_GET_SETTING_STR("setup.web.url", buffer));
		running = ZOS_TRUE;

    }
    else{
    	ZOS_LOG("Pinging...");
    	zn_issue_command_return_str(buffer2,sizeof(buffer2)-1,"ping -g");
    	ZOS_LOG("obtained %s",buffer2);
    	if(strcmp(buffer2,"Ping failed")==0){
    	    setup_done=0;
    	    zn_nvm_write(&setup_done,20,4);
    	    zn_nvm_save(NULL);
    	    zn_system_reboot();
    	    return;
    	   }
    	zn_network_register_softap_event_handler(softap_event_handler);
    	if(ZOS_FAILED(result, zn_network_up(ZOS_SOFTAP, ZOS_TRUE))){
    	    	ZOS_LOG("Failed to start SoftAP: %d", result);
    	    	setup_done=0;
    	    	zn_nvm_write(&setup_done,20,4);
    	    	zn_nvm_save(NULL);
    	    	zn_system_reboot();
    	    	return;
    	    }
    }
}

/*************************************************************************************/

static void softap_event_handler(const zos_softap_client_t *info)
{
    char mac_str[32];
    char ip_str[32];
    ZOS_LOG("SoftAP Client: %s (%s) - %sonnected", mac_to_str(&info->mac_address, mac_str),
                                                   ip_to_str(info->ip_address, ip_str),
                                                   info->connected ? "C" : "Disc");
}

/*************************************************************************************************/
void zn_app_deinit(void)
{
    // stop web setup again just in case it isn't already stopped
    zn_setup_stop();
    // clean up the event handlers
    zn_setup_register_client_event_handler(NULL);
    zn_setup_register_finished_event_handler(NULL);

    ZOS_LOG("Web Setup App complete");
}


/*************************************************************************************************/
zos_bool_t zn_app_idle(void)
{
    return running;
}


/*************************************************************************************************/
static void setup_client_event_handler(const zos_softap_client_t *client)
{
    char buffer[32];

    if(client->connected)
    {
        // If the OS is 'invalid' then that means the client has connected to the SoftAP but NOT
        // the HTTP server yet
        if(client->additional == SETUP_OS_INVALID)
        {
            ZOS_LOG("Client connected: %s - %s", mac_to_str(&client->mac_address, NULL), ip_to_str(client->ip_address, buffer));
        }
        else
        {
            ZOS_LOG("Client connected to server: %s - %s",  ip_to_str(client->ip_address, buffer), zn_setup_get_client_os_str(client));
        }
    }
    else
    {
        ZOS_LOG("Client disconnected: %s - %s", mac_to_str(&client->mac_address, NULL), ip_to_str(client->ip_address, buffer));
    }
}


/*************************************************************************************************/
static void setup_finished_event_handler(void *unused)
{
    ZOS_LOG("Web setup finished");
    uint32_t setup_done=1;
    zn_nvm_write(&setup_done,20,4);
    zn_nvm_save(NULL);
    running = ZOS_FALSE;
}
