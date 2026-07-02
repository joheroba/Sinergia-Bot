import React, { useRef, useState, useEffect } from 'react';
import { StyleSheet, BackHandler, Platform, View, ActivityIndicator, TouchableOpacity, Text, Modal, TextInput, ScrollView, KeyboardAvoidingView } from 'react-native';
import { WebView } from 'react-native-webview';
import { SafeAreaView, SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';
import { Ionicons } from '@expo/vector-icons';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
  }

  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return;
    }
    try {
      const projectId = Constants.expoConfig?.extra?.eas?.projectId || Constants.easConfig?.projectId;
      token = (await Notifications.getExpoPushTokenAsync({
        projectId,
      })).data;
    } catch (e) {
      console.log(e);
    }
  }

  return token;
}

export default function App() {
  const webViewRef = useRef<WebView>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const [canGoBack, setCanGoBack] = useState(false);
  const [expoPushToken, setExpoPushToken] = useState<string | undefined>('');
  
  // Estado del Chat
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState<{role: string, text: string}[]>([
    { role: 'assistant', text: '¡Hola! Soy GanoiBot, ¿en qué te puedo ayudar hoy con Gano iTouch?' }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  // Endpoint de AethelOS en la nube VPS
  const API_URL = "http://45.55.92.211:3000/api/chat";

  useEffect(() => {
    registerForPushNotificationsAsync().then(token => setExpoPushToken(token));

    const onBackPress = () => {
      if (isChatOpen) {
        setIsChatOpen(false);
        return true;
      }
      if (canGoBack && webViewRef.current) {
        webViewRef.current.goBack();
        return true;
      }
      return false;
    };

    const subscription = BackHandler.addEventListener('hardwareBackPress', onBackPress);

    return () => {
      subscription.remove();
    };
  }, [canGoBack, isChatOpen]);

  const sendMessage = async () => {
    if (!inputText.trim()) return;
    
    const userMsg = inputText.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInputText('');
    setIsTyping(true);
    
    // Auto-scroll
    setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, userId: expoPushToken || 'user-mobile-1', agent: 'GanoiBot' })
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.reply || 'Hubo un error al procesar la respuesta.' }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', text: '❌ Error de conexión con GanoiBot.' }]);
    } finally {
      setIsTyping(false);
      setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  const injectedJavascript = `
    window.EXPO_PUSH_TOKEN = '${expoPushToken || ''}';
    true;
  `;

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" backgroundColor="#0f172a" />
        <View style={styles.welcomeContainer}>
          <Ionicons name="rocket-outline" size={80} color="#8b5cf6" />
          <Text style={styles.welcomeTitle}>SinergiaBot</Text>
          <Text style={styles.welcomeSubtitle}>Tu mentor potenciado con IA para Gano iTouch</Text>
          <Text style={styles.welcomeFooter}>Toca el botón flotante para comenzar el chat</Text>
        </View>
        
        {/* Floating Action Button for GanoiBot */}
        {!isChatOpen && (
          <TouchableOpacity style={styles.fab} onPress={() => setIsChatOpen(true)}>
            <Ionicons name="chatbubbles" size={28} color="#fff" />
          </TouchableOpacity>
        )}

        {/* Chat Modal */}
        <Modal visible={isChatOpen} animationType="slide" transparent={true}>
          <View style={styles.modalContainer}>
            <View style={styles.chatHeader}>
              <Text style={styles.chatTitle}>GanoiBot (Gano iTouch)</Text>
              <TouchableOpacity onPress={() => setIsChatOpen(false)}>
                <Ionicons name="close" size={28} color="#fff" />
              </TouchableOpacity>
            </View>
            
            <ScrollView ref={scrollViewRef} style={styles.chatBody} contentContainerStyle={{ paddingBottom: 20 }}>
              {messages.map((msg, index) => (
                <View key={index} style={msg.role === 'user' ? styles.msgUser : styles.msgAssistant}>
                  <Text style={msg.role === 'user' ? styles.msgTextUser : styles.msgTextAssistant}>{msg.text}</Text>
                </View>
              ))}
              {isTyping && (
                <View style={styles.msgAssistant}>
                  <ActivityIndicator size="small" color="#0f172a" />
                </View>
              )}
            </ScrollView>
            
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
              <View style={styles.chatInputContainer}>
                <TextInput 
                  style={styles.chatInput} 
                  placeholder="Escribe un mensaje..." 
                  value={inputText}
                  onChangeText={setInputText}
                  onSubmitEditing={sendMessage}
                />
                <TouchableOpacity style={styles.sendButton} onPress={sendMessage}>
                  <Ionicons name="send" size={20} color="#fff" />
                </TouchableOpacity>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>

      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  welcomeContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  welcomeTitle: { color: '#fff', fontSize: 32, fontWeight: 'bold', marginTop: 20 },
  welcomeSubtitle: { color: '#94a3b8', fontSize: 18, textAlign: 'center', marginTop: 10, marginBottom: 40 },
  welcomeFooter: { color: '#475569', fontSize: 14, textAlign: 'center', position: 'absolute', bottom: 100 },
  loadingContainer: { ...StyleSheet.absoluteFillObject, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0f172a' },
  fab: {
    position: 'absolute',
    bottom: 30,
    right: 20,
    backgroundColor: '#8b5cf6', // Purple color for GanoiBot
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 5
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#f1f5f9',
    marginTop: 50,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    elevation: 20,
    shadowColor: '#000',
    shadowOpacity: 0.5,
    shadowOffset: { width: 0, height: -5 },
    shadowRadius: 10
  },
  chatHeader: {
    backgroundColor: '#8b5cf6',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  chatTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  chatBody: { flex: 1, padding: 15 },
  msgUser: {
    alignSelf: 'flex-end',
    backgroundColor: '#3b82f6',
    padding: 12,
    borderRadius: 15,
    borderBottomRightRadius: 0,
    marginBottom: 10,
    maxWidth: '80%'
  },
  msgAssistant: {
    alignSelf: 'flex-start',
    backgroundColor: '#e2e8f0',
    padding: 12,
    borderRadius: 15,
    borderBottomLeftRadius: 0,
    marginBottom: 10,
    maxWidth: '80%'
  },
  msgTextUser: { color: '#fff', fontSize: 16 },
  msgTextAssistant: { color: '#0f172a', fontSize: 16 },
  chatInputContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderColor: '#e2e8f0'
  },
  chatInput: {
    flex: 1,
    backgroundColor: '#f1f5f9',
    borderRadius: 20,
    paddingHorizontal: 15,
    fontSize: 16,
    maxHeight: 100
  },
  sendButton: {
    backgroundColor: '#8b5cf6',
    width: 45,
    height: 45,
    borderRadius: 22.5,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 10
  }
});
