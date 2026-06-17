namespace SimpleVpnClient.Models;

public class VpnServer
{
    public string Name { get; set; }        // "Германия-1"
    public string Country { get; set; }     // "DE"
    public string ConfigJson { get; set; }  // полный JSON конфиг для sing-box
    public int Ping { get; set; }           // задержка в мс
    
    public override string ToString()
    {
        return $"{Country} | {Name} | {Ping}ms";
    }
}
