import { NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    console.log('Received messages:', messages);
    
    // Get the last message from the user
    const lastMessage = messages[messages.length - 1];
    console.log('Sending to backend:', lastMessage.content);
    
    // Forward the request to the FastAPI backend
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: lastMessage.content
      }),
    });

    if (!response.ok) {
      console.error('Backend error:', response.status, await response.text());
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Backend response:', data);
    
    // Return a simple JSON response
    return NextResponse.json({
      response: data.response,
      confidence: data.confidence,
      source: data.source
    });
  } catch (error) {
    console.error('Error in chat route:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
