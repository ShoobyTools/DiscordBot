// prefixRegex, _ := regexp.Compile(`(\d+\.){3}`)
// suffixRegex, _ := regexp.Compile("(:.+){2,3}")
// prefix := prefixRegex.FindString(ip)
// suffix := suffixRegex.FindString(ip)
// if prefix == "" {
//     return [256]string{}, errors.New("improperly formatted IP address")
// }
// ipRange := [256]string{}
// for i := 0; i < 256; i++ {
//     ipRange[i] = fmt.Sprintf("%s%d%s", prefix, i, suffix)
// }