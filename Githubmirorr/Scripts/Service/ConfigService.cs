using System.Net.Http.Json;
using SimpleVpnClient.Models;

namespace SimpleVpnClient.Services;

public class ConfigService
{
    private readonly HttpClient _http;
    
    // ВАЖНО: замени на свой API или на открытый источник конфигов
    private const string API_URL = "https://api.your-vpn-server.com/servers";

    public ConfigService()
    {
        _http = new HttpClient
        {
            Timeout = TimeSpan.FromSeconds(10)
        };
    }

    /// <summary>
    /// Получает список доступных серверов с API
    /// </summary>
    public async Task<List<VpnServer>> GetServersAsync()
    {
        try
        {
            // Делаем GET запрос к API
            var servers = await _http.GetFromJsonAsync<List<VpnServer>>(API_URL);
            return servers ?? new List<VpnServer>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Ошибка получения серверов: {ex.Message}");
            return new List<VpnServer>();
        }
    }

    /// <summary>
    /// Парсит подписку (subscription link) — base64 список серверов
    /// Например, из открытых каналов Telegram
    /// </summary>
    public async Task<List<VpnServer>> ParseSubscriptionAsync(string subUrl)
    {
        try
        {
            var base64 = await _http.GetStringAsync(subUrl);
            var decoded = System.Text.Encoding.UTF8.GetString(
                Convert.FromBase64String(base64));
            
            // decoded содержит список ссылок типа:
            // vless://uuid@ip:port?params#Name
            // vmess://base64json
            // Распарси и конвертируй в VpnServer + ConfigJson
            
            // Это упрощённый пример
            return new List<VpnServer>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Ошибка парсинга подписки: {ex.Message}");
            return new List<VpnServer>();
        }
    }
}
